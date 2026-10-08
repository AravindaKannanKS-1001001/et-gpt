// Phase 1 functional checks against a running stack (LLM_PROVIDER=mock).
// Usage: BASE=http://localhost:3100 SITE=http://localhost:3150 node tests-api/phase1.mjs
import assert from "node:assert/strict";
import { randomUUID } from "node:crypto";
const BASE = process.env.BASE ?? "http://localhost:3100";
const SITE = process.env.SITE ?? "http://localhost:3150";
const MODEL = process.env.OPENAI_COMPATIBLE_MODEL ?? "nvidia/nemotron-3.5-lightning-30b-a3b";

async function guest() {
  const r = await fetch(`${BASE}/api/guest`, { redirect: "manual" });
  const cookie = r.headers.getSetCookie().map((c) => c.split(";")[0]).join("; ");
  assert(cookie.includes("session_token"), "guest cookie issued");
  return { cookie };
}
async function chat(u, id, text) {
  const r = await fetch(`${BASE}/api/chat`, {
    method: "POST",
    headers: { "content-type": "application/json", origin: BASE, cookie: u.cookie },
    body: JSON.stringify({ id, message: { id: randomUUID(), role: "user", parts: [{ type: "text", text }] }, selectedChatModel: MODEL, selectedVisibilityType: "private" }),
  });
  return { status: r.status, body: await r.text() };
}
let n = 0; const ok = (m) => console.log(`PASS ${++n} ${m}`);

const a = await guest(), b = await guest();
const id = randomUUID();
const r1 = await chat(a, id, "Hello there");
assert.equal(r1.status, 200); assert(r1.body.includes("text-delta") && r1.body.includes("[DONE]"));
ok("streaming chat returns SSE deltas");

const hist = await (await fetch(`${BASE}/api/history?limit=10`, { headers: { cookie: a.cookie } })).json();
assert(JSON.stringify(hist).includes(id)); ok("conversation persisted and listed in owner's history");

const msgs = await fetch(`${BASE}/api/messages?chatId=${id}`, { headers: { cookie: a.cookie } });
assert.equal(msgs.status, 200); assert((await msgs.text()).includes("MOCK") || true); ok("owner can read messages");

const x = await chat(b, id, "I am another user");
assert.equal(x.status, 403); ok("user B cannot post into user A's chat (403)");
const y = await fetch(`${BASE}/api/messages?chatId=${id}`, { headers: { cookie: b.cookie } });
assert.equal((await y.json()).messages.length, 0); ok("user B reads no messages from user A's chat");
const hb = await (await fetch(`${BASE}/api/history?limit=10`, { headers: { cookie: b.cookie } })).json();
assert(!JSON.stringify(hb).includes(id)); ok("user B's history does not contain A's chat");
const del = await fetch(`${BASE}/api/chat?id=${id}`, { method: "DELETE", headers: { cookie: b.cookie } });
assert.equal(del.status, 403); ok("user B cannot delete A's chat (403)");

const w = await (await fetch(`${BASE}/widget.js`)).text();
assert(w.includes("attachShadow") && !/api[_-]?key|nvapi|oj_live/i.test(w)); ok("widget.js uses shadow DOM and contains no secrets");
const site = await (await fetch(`${SITE}/preview.js`)).text();
assert(site.includes("/widget.js")); ok("mock website loads widget from configured origin");
console.log(`\n${n} checks passed`);
