import Ajv from "ajv";

const ajv = new Ajv({ allErrors: true, strict: false });

/** Numbers/words the customer actually typed, used to ground form prefill. */
export function statedNumbers(texts: string[]): string[] {
  return texts.flatMap((t) => t.match(/(?<![\w.])-?\d+(?:\.\d+)?/g) ?? []);
}

/**
 * Keep a prefill value only if the customer stated it; each stated number may
 * fill ONE input. Everything else is dropped (the form shows a blank).
 */
export function groundArgs(prefill: Record<string, unknown>, stated: string[]) {
  const pool = [...stated];
  const args: Record<string, unknown> = {};
  const dropped: string[] = [];
  for (const [k, v] of Object.entries(prefill)) {
    if (typeof v === "number") {
      const i = pool.findIndex((s) => Number(s) === v);
      if (i >= 0) {
        pool.splice(i, 1);
        args[k] = v;
        continue;
      }
      dropped.push(k);
    } else if (typeof v === "string" && v.trim()) {
      args[k] = v;
    }
  }
  return { args, dropped };
}

export type Schema = { type?: string; properties?: Record<string, unknown>; required?: string[] };

/** Validate submitted form args against the formula's real input schema. */
export function validateArgs(schema: Schema, args: Record<string, unknown>) {
  const ok = ajv.validate({ ...schema, additionalProperties: false }, args);
  return ok ? null : ajv.errorsText(ajv.errors, { dataVar: "input" });
}
