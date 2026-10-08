import assert from "node:assert/strict";
import { groundArgs, statedNumbers, validateArgs } from "../lib/calc";

// Replay of a reported failure: user said "3.5 mm, 100mm, 45mm"; model invented
// sensor 7 and copied 100 into a second input. Invented values are blanked and
// one stated number fills one input.
const stated = statedNumbers(["3.5 mm, 100mm, 45mm"]);
assert.deepEqual(stated, ["3.5", "100", "45"]);
const g = groundArgs({ sensor_size_mm: 7, working_distance_mm: 100, focal_length_mm: 100, note: "hi" }, stated);
assert.deepEqual(g.args, { note: "hi", working_distance_mm: 100 });
assert.deepEqual(g.dropped.sort(), ["focal_length_mm", "sensor_size_mm"]);
assert.deepEqual(groundArgs({ a: 5 }, []).args, {}); // nothing stated => blank form

const schema = { properties: { a: { type: "number", exclusiveMinimum: 0 }, b: { type: "number" } }, required: ["a", "b"], type: "object" };
assert.equal(validateArgs(schema, { a: 1, b: 2 }), null);
assert.notEqual(validateArgs(schema, { a: 1 }), null); // missing required
assert.notEqual(validateArgs(schema, { a: -1, b: 2 }), null); // exclusiveMinimum
assert.notEqual(validateArgs(schema, { a: "x", b: 2 }), null); // type
assert.notEqual(validateArgs(schema, { a: 1, b: 2, evil: 1 }), null); // unknown field
console.log("calc ok");
