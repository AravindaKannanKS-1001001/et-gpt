---
name: calc-then-catalog
description: Chain a calculation into a catalog search - derive a requirement (e.g. focal length) and narrow lens/product lookups with the approved result.
---
# Calculation, then catalog

1. Call `createPlan` first: knowledge/lookups -> calculation inputs -> calculation -> catalog narrowing -> answer.
2. Gather missing facts with read-only tools (`search_knowledge_base`, `lookup`, `get_reference`). If a needed input is still unknown, say exactly which one and ask.
3. Run the calculation with the `calc-with-approval` skill. Do not skip approval.
4. Use the approved result to narrow the catalog: `list_families` / `describe_table` / `search_products` with filters derived from the result. Keep exact numbers and units.
5. If several families or tables are plausible, check each grounded candidate (do not drop options silently). Summarise results side by side and explain trade-offs (e.g. focal length vs. sensor coverage vs. mount).
6. Never call a lens "best" without evidence. Never state prices; refer to the contact page.
