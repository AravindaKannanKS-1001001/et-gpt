import assert from "node:assert/strict";
import { maskPrices, priceMaskTransform } from "../lib/guardrails";
async function run(parts: string[]) {
  const t = priceMaskTransform()();
  const w = t.writable.getWriter(); const r = t.readable.getReader();
  const out: string[] = [];
  (async () => { for (const p of parts) await w.write({ type: "text-delta", id: "a", text: p }); await w.write({ type: "text-end", id: "a" }); await w.close(); })();
  for (;;) { const { done, value } = await r.read(); if (done) break; if (value.type === "text-delta") out.push(value.text!); }
  return out.join("");
}
assert.equal(await run(["The price is $5", "00 only"]), "The price is [price not shown] only");
assert.equal(await run(["Costs USD", " 500 per unit."]), "Costs [price not shown] per unit.");
assert.equal(await run(["It costs Rs. 1,200", " today"]), "It costs [price not shown] today");
assert.equal(await run(["Focal length is 16 mm and FOV 100 mm."]), "Focal length is 16 mm and FOV 100 mm.");
assert.equal(maskPrices("₹ 500 and 20 dollars"), "[price not shown] and [price not shown]");
console.log("guardrail ok");
