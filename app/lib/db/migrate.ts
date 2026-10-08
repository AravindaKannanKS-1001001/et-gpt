import { config } from "dotenv";
import { drizzle } from "drizzle-orm/postgres-js";
import { migrate } from "drizzle-orm/postgres-js/migrator";
import postgres from "postgres";

config({ path: ".env.local" });

// Migrations run as the owner (POSTGRES_URL_ADMIN). The app itself connects as
// the restricted role "et_app" (POSTGRES_URL), which RLS applies to.
const APP_TABLES = [
  "Chat",
  "Message_v2",
  "Vote_v2",
  "Stream",
  "Document",
  "Suggestion",
];

const runMigrate = async () => {
  const url = process.env.POSTGRES_URL_ADMIN;
  if (!url) {
    console.log("POSTGRES_URL_ADMIN not defined, skipping migrations");
    process.exit(0);
  }
  const sql = postgres(url, { max: 1 });
  const db = drizzle(sql);

  console.log("Running migrations...");
  const start = Date.now();
  await migrate(db, { migrationsFolder: "./lib/db/migrations" });

  const appPassword = process.env.APP_DB_PASSWORD;
  if (!appPassword) {
    throw new Error("APP_DB_PASSWORD is required to create the et_app role");
  }
  const [{ exists }] = await sql`select exists(select 1 from pg_roles where rolname = 'et_app') as exists`;
  const pw = appPassword.replace(/'/g, "''");
  await sql.unsafe(
    `${exists ? "ALTER" : "CREATE"} ROLE et_app LOGIN NOBYPASSRLS NOSUPERUSER PASSWORD '${pw}'`
  );
  const dbName = new URL(url).pathname.slice(1);
  await sql.unsafe(`GRANT CONNECT ON DATABASE "${dbName}" TO et_app`);
  await sql.unsafe("GRANT USAGE ON SCHEMA public TO et_app");
  await sql.unsafe(
    `GRANT SELECT, INSERT, UPDATE, DELETE ON ${APP_TABLES.map((t) => `"${t}"`).join(", ")} TO et_app`
  );
  console.log("Migrations completed in", Date.now() - start, "ms");
  await sql.end();
  process.exit(0);
};

runMigrate().catch((err) => {
  console.error("Migration failed");
  console.error(err);
  process.exit(1);
});
