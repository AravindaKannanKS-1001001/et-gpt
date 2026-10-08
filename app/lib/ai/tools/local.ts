import { tool } from "ai";
import { z } from "zod";
import { groundArgs, type Schema, statedNumbers } from "@/lib/calc";
import { parseToolResult } from "@/lib/mcp";
import { loadSkills } from "@/lib/skills";

export const createPlan = tool({
  description:
    "Write the ordered plan for a multi-step request BEFORE doing the steps. Shown to the customer.",
  execute: async ({ goal, steps }) => ({ goal, steps }),
  inputSchema: z.object({
    goal: z.string().max(300),
    steps: z
      .array(
        z.object({
          area: z.enum(["knowledge", "calculation", "catalog", "clarify", "answer"]),
          title: z.string().max(200),
        })
      )
      .min(1)
      .max(8),
  }),
});

export const loadSkill = tool({
  description: "Read a skill's full instructions by name.",
  execute: async ({ name }) => {
    const s = loadSkills().find((x) => x.name === name);
    return s ? { body: s.body, name: s.name } : { error: `Unknown skill: ${name}` };
  },
  inputSchema: z.object({ name: z.string() }),
});

/**
 * Prepares the approval form. It never runs the calculation: the customer edits
 * and approves in the UI, and the server executes after validating the input.
 * `prefill` is grounded against what the customer actually typed.
 */
export function proposeCalculation(opts: {
  call: (name: string, args: Record<string, unknown>) => Promise<unknown>;
  userTexts: string[];
}) {
  return tool({
    description:
      "Show the customer an editable calculation form for a formula. Prefill ONLY values the customer stated. Ends your turn; do not run the calculation yourself.",
    execute: async ({ formula_id, prefill }) => {
      let def: { input_schema?: Schema; description?: string; error?: unknown } | undefined;
      try {
        def = parseToolResult(await opts.call("get_calculator", { formula_id })) as typeof def;
      } catch {
        def = undefined;
      }
      if (!def?.input_schema || def.error) {
        return { error: `Unknown or unavailable formula: ${formula_id}` };
      }
      const { args, dropped } = groundArgs(prefill ?? {}, statedNumbers(opts.userTexts));
      return {
        description: def.description ?? null,
        dropped,
        formula_id,
        prefill: args,
        schema: def.input_schema,
      };
    },
    inputSchema: z.object({
      formula_id: z.string(),
      prefill: z.record(z.string(), z.union([z.number(), z.string()])).optional(),
    }),
  });
}
