// Dev-only Postgres without Docker (Docker compose is used for real deployments).
import EmbeddedPostgres from "embedded-postgres";
import { existsSync } from "node:fs";

const dir = ".devdb";
const pg = new EmbeddedPostgres({ databaseDir: dir, user: "etgpt", password: "etgpt", port: 5433, persistent: true, initdbFlags: ["--encoding=UTF8", "--locale=C"] });
if (!existsSync(`${dir}/PG_VERSION`)) {
  await pg.initialise();
}
await pg.start();
try { await pg.createDatabase("etgpt"); } catch {}
console.log("postgres ready: postgres://etgpt:etgpt@localhost:5433/etgpt");
process.on("SIGINT", async () => { await pg.stop(); process.exit(0); });
setInterval(() => {}, 1 << 30);
