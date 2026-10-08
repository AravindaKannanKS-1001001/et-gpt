// Creates (or promotes) the first admin from ADMIN_EMAIL / ADMIN_PASSWORD.
// Run: pnpm exec tsx scripts/seed-admin.ts   (admin is never self-service)
import { config } from "dotenv";
config({ path: ".env.local" });

async function main() {
  const { authServer } = await import("../lib/auth");
  const { adminSql } = await import("../lib/db/admin");

  const email = process.env.ADMIN_EMAIL;
  const password = process.env.ADMIN_PASSWORD;
  if (!(email && password)) {
    throw new Error("Set ADMIN_EMAIL and ADMIN_PASSWORD");
  }
  const [existing] = await adminSql`select id from "User" where email = ${email}`;
  if (!existing) {
    await authServer.api.signUpEmail({ body: { email, name: "Admin", password } });
  }
  await adminSql`update "User" set role = 'admin', "emailVerified" = true where email = ${email}`;
  console.log(`admin ready: ${email}`);
  await adminSql.end();

}
main().then(() => process.exit(0), (e) => { console.error(e); process.exit(1); });
