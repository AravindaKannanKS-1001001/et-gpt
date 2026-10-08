# Skills (SKILL.md format)

Skills live in `app/skills/<name>/SKILL.md` (frontmatter `name`, `description`; body = instructions). The model sees only the name + description list in its system prompt and calls `loadSkill(name)` to read the body when needed (progressive disclosure, same convention as Anthropic Agent Skills). Parsed with `gray-matter` in `app/lib/skills.ts`.

They were extracted from the behaviours the old suite's tests encoded (`chatbot/tests/workflow.ts`, `hitl.ts`, etc.) and from how all three MCP servers chain together.

| Skill | Purpose | Distilled from |
|---|---|---|
| `calc-with-approval` | Find formula by the quantity to FIND, read the real input schema, show an editable form with only user-stated values, stop, continue after approval; cancel runs nothing; approval is single-use | `hitl.ts`, `workflow.ts` (grounded prefill, cancel is inert, pending form does not break follow-ups) |
| `calc-then-catalog` | Plan first, gather inputs, run the approved calculation, narrow the catalog with the exact result, check every grounded candidate, compare trade-offs, no prices | `workflow.ts` (calculation -> catalog -> answer loop) |
| `ambiguous-requests` | Ask one clarifying question instead of guessing; reuse known facts; explain terms | SRS section 4.1 |
| `lens-selection` | Establish sensor/distance/FOV meaning, locate the table/family, search every grounded family, present honest comparison | catalog server tools (`lookup_model`, `describe_table`, `search_products`) |

Enforcement does not rely on the skills alone: the server verifies the form answer, validates inputs against the formula's schema, and executes `calculate` itself (see SRS 4.2).
