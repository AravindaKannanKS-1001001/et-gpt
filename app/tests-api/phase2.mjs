// Phase 2: auth, roles, quotas, isolation, RLS. Needs the app on BASE with LLM_PROVIDER=mock
// and .env.local (reads DB URLs, admin creds, DEV_MAIL_DIR). Run: node tests-api/phase2.mjs
import assert from "node:assert/strict";
import { randomUUID } from "node:crypto";
import { readFileSync } from "node:fs";
import postgres from "postgres";
import { config } from "dotenv";
config({ path: ".env.local", quiet: true });

const BASE = process.env.BASE ?? "http://localhost:3100";
const MODEL = process.env.OPENAI_COMPATIBLE_MODEL;
const admin = postgres(process.env.POSTGRES_URL_ADMIN, { max: 1 });
const app = postgres(process.env.POSTGRES_URL, { max: 1 });
const H = { "content-type": "application/json", origin: BASE };
let n = 0;
const ok = (m) => console.log(`PASS ${++n} ${m}`);
const jar = (r) => r.headers.getSetCookie().map((c) => c.split(";")[0]).join("; ");
const clearRates = async () => {
  await admin`delete from rate_limits`;
  await admin`delete from "AuthRateLimit"`;
};

async function guest() {
  const r = await fetch(`${BASE}/api/guest`, { redirect: "manual" });
  assert.equal(r.status, 307, `guest status ${r.status}`);
  const cookie = jar(r);
  assert(cookie.includes("session_token"));
  return cookie;
}
const chat = (cookie, id = randomUUID(), text = "Hello there") =>
  fetch(`${BASE}/api/chat`, {
    method: "POST",
    headers: { ...H, cookie },
    body: JSON.stringify({
      id,
      message: { id: randomUUID(), role: "user", parts: [{ type: "text", text }] },
      selectedChatModel: MODEL,
      selectedVisibilityType: "private",
    }),
  }).then(async (r) => ({ status: r.status, retry: r.headers.get("retry-after"), body: await r.text(), id }));
const get = (cookie, path) => fetch(`${BASE}${path}`, { headers: { cookie }, redirect: "manual" });

async function verifiedUser(prefix) {
  const email = `${prefix}-${Date.now()}@example.com`;
  const password = "Str0ng-pass-1";
  let r = await fetch(`${BASE}/api/auth/sign-up/email`, { method: "POST", headers: H, body: JSON.stringify({ email, password, name: prefix }) });
  assert.equal(r.status, 200, await r.text());
  await new Promise((x) => setTimeout(x, 500));
  r = await fetch(`${BASE}/api/auth/sign-in/email`, { method: "POST", headers: H, body: JSON.stringify({ email, password }) });
  assert.equal(r.status, 403); // unverified cannot sign in
  const link = readFileSync(`${process.env.DEV_MAIL_DIR}/${email}.txt`, "utf8");
  r = await fetch(link, { redirect: "manual" });
  assert([200, 302, 307].includes(r.status), `verify ${r.status}`);
  r = await fetch(`${BASE}/api/auth/sign-in/email`, { method: "POST", headers: H, body: JSON.stringify({ email, password }) });
  assert.equal(r.status, 200);
  return { email, password, cookie: jar(r) };
}
async function signIn(email, password, cookie = "") {
  const r = await fetch(`${BASE}/api/auth/sign-in/email`, { method: "POST", headers: { ...H, cookie }, body: JSON.stringify({ email, password }) });
  assert.equal(r.status, 200, await r.text());
  return jar(r);
}

await clearRates();

// --- identity & roles
const g = await guest();
ok("anonymous guest session issued");
assert.equal((await fetch(`${BASE}/api/history`)).status, 401);
ok("no session -> 401 on API");
const v = await verifiedUser("verified");
ok("registered user is blocked until email verified, then can sign in");

// --- quotas
let r = await chat(g);
assert.equal(r.status, 200);
r = await chat(g);
assert.equal(r.status, 200);
r = await chat(g);
assert.equal(r.status, 429);
assert(Number(r.retry) > 0);
ok(`guest per-minute limit: 3rd request in a minute -> 429 (Retry-After ${r.retry}s)`);
for (let i = 0; i < 3; i++) {
  await admin`delete from rate_limits where key like 'min:%'`;
  r = await chat(g);
  assert.equal(r.status, 200, `req ${i + 3}`);
}
await admin`delete from rate_limits where key like 'min:%'`;
r = await chat(g);
assert.equal(r.status, 429);
assert(r.body.includes("today"));
ok("guest per-day limit: 6th request of the day -> 429");
await clearRates();
for (let i = 0; i < 5; i++) {
  r = await chat(v.cookie);
  assert.equal(r.status, 200);
}
r = await chat(v.cookie);
assert.equal(r.status, 429);
ok("verified user per-minute limit is 5 (6th -> 429)");
await clearRates();

// --- permissions
const form = (type) => {
  const f = new FormData();
  f.append("file", new Blob(["x"], { type }), "a.txt");
  return f;
};
let u = await fetch(`${BASE}/api/files/upload`, { method: "POST", headers: { cookie: g }, body: form("text/plain") });
assert.equal(u.status, 403);
ok("guest upload -> 403 (denied server-side)");
u = await fetch(`${BASE}/api/files/upload`, { method: "POST", headers: { cookie: v.cookie }, body: form("text/plain") });
assert.equal(u.status, 400);
ok("verified user passes authorization (reaches validation -> 400)");

// --- isolation (API + RLS)
const A = await guest();
const B = await guest();
const idA = randomUUID();
r = await chat(A, idA);
assert.equal(r.status, 200);
assert.equal((await chat(B, idA)).status, 403);
const peek = await get(B, `/api/messages?chatId=${idA}`);
assert.equal((await peek.json()).messages.length, 0);
assert([403, 404].includes((await fetch(`${BASE}/api/chat?id=${idA}`, { method: "DELETE", headers: { cookie: B } })).status));
assert(!(await (await get(B, "/api/history?limit=20")).text()).includes(idA));
ok("API: user B cannot post to, read, delete or list user A's chat");

const [{ uid: uidA }] = await admin`select "userId" as uid from "Chat" where id=${idA}`;
const [{ uid: uidB }] = await admin`select id as uid from "User" where id <> ${uidA} and "isAnonymous" order by "createdAt" desc limit 1`;
const asUser = (uid, role = "user") =>
  app.begin(async (tx) => {
    await tx`select set_config('app.user_id', ${uid}, true), set_config('app.role', ${role}, true)`;
    return {
      chats: await tx`select id from "Chat" where id=${idA}`,
      msgs: await tx`select count(*)::int as c from "Message_v2" where "chatId"=${idA}`,
    };
  });
assert.equal((await app`select count(*)::int as c from "Chat"`)[0].c, 0);
ok("RLS: no principal -> 0 rows (fail closed)");
const own = await asUser(uidA);
assert.equal(own.chats.length, 1);
assert(own.msgs[0].c >= 2);
const other = await asUser(uidB);
assert.equal(other.chats.length, 0);
assert.equal(other.msgs[0].c, 0);
ok("RLS: owner sees own chat+messages; another user sees none (direct SQL as et_app)");
assert.equal((await asUser(uidB, "admin")).chats.length, 1);
const wrote = await app.begin(async (tx) => {
  await tx`select set_config('app.user_id', ${uidB}, true), set_config('app.role','admin',true)`;
  const res = await tx`update "Chat" set title='pwned' where id=${idA}`;
  return res.count;
});
assert.equal(wrote, 0);
ok("RLS: admin may read but cannot modify another user's chat");
await assert.rejects(app`select * from "Session"`);
await assert.rejects(app`select * from "Account"`);
ok("et_app role cannot read Session/Account tables");

// --- guest -> verified keeps chats
const gc = await guest();
const idG = randomUUID();
assert.equal((await chat(gc, idG)).status, 200);
await clearRates();
const merged = await signIn(v.email, v.password, gc);
assert((await (await get(merged, "/api/history?limit=50")).text()).includes(idG));
ok("guest chats move to the account on sign-in");

// --- admin
await clearRates();
const adminCookie = await signIn(process.env.ADMIN_EMAIL, process.env.ADMIN_PASSWORD);
assert.equal((await get(adminCookie, "/api/admin/stats")).status, 200);
assert.equal((await get(g, "/api/admin/stats")).status, 403);
assert.equal((await get(v.cookie, "/api/admin/stats")).status, 403);
assert.equal((await fetch(`${BASE}/api/admin/stats`)).status, 401);
ok("admin route: admin 200, user 403, guest 403, anonymous 401");

// --- guest abuse: sessions per IP
await clearRates();
let blocked = 0;
for (let i = 0; i < 12; i++) {
  const x = await fetch(`${BASE}/api/guest`, { redirect: "manual" });
  if (x.status === 429) blocked++;
}
assert(blocked >= 2);
ok(`guest-session creation capped per IP (${blocked} of 12 blocked)`);
await clearRates();

console.log(`\n${n} checks passed`);
await admin.end();
await app.end();
process.exit(0);
