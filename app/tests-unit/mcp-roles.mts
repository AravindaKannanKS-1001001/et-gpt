// Role filtering at discovery and at call time, against the real MCP server.
import { config } from "dotenv";
config({ path: ".env.local", quiet: true });
import assert from "node:assert/strict";
import { randomUUID } from "node:crypto";

const { openMcp } = await import("../lib/mcp");
const { adminSql } = await import("../lib/db/admin");
const uid = randomUUID();

const guest = await openMcp("guest", uid);
const user = await openMcp("user", uid);
const admin = await openMcp("admin", uid);
assert(guest.discovered.length >= 17, `discovered ${guest.discovered.length}`);
for (const [who, s] of [["guest", guest], ["user", user]] as const) {
  assert(!("calculate" in s.tools), `${who} must not see calculate`);
  assert(!("run_select" in s.tools), `${who} must not see run_select`);
  assert("search_knowledge_base" in s.tools && "search_calculator" in s.tools && "search_products" in s.tools);
}
assert(!("calculate" in admin.tools), "calculate is never offered to the model, even to admins");
assert("run_select" in admin.tools, "admin sees run_select");

// server-initiated calls are permission-checked again
await assert.rejects(guest.call("calculate", { formula_id: "focal_length", args: {} }), /forbidden/);
await assert.rejects(user.call("run_select", { sql: "select 1" }), /forbidden/);
const ok = await user.call("calculate", { formula_id: "focal_length", args: { object_size_mm: 100, working_distance_mm: 300, sensor_size_mm: 8.8 } });
assert(ok);
const rows = await adminSql`select tool, ok from "ToolLog" where "userId" = ${uid} order by "createdAt"`;
assert(rows.some((r) => r.tool === "calculate" && r.ok), "approved call audited");
assert(rows.filter((r) => !r.ok).length >= 2, "denied calls audited");
await Promise.all([guest.close(), user.close(), admin.close()]);
await adminSql.end();
console.log("mcp roles ok:", guest.discovered.length, "tools discovered;", Object.keys(guest.tools).length, "visible to guest/user;", Object.keys(admin.tools).length, "to admin");
process.exit(0);
