---
name: lens-selection
description: Pick candidate lenses from the catalog and compare them honestly.
---
# Lens selection

1. Establish: sensor size, working distance, field of view (whole area vs smallest feature), mount, resolution. Ask for what is missing.
2. Use `lookup_model` / `search_knowledge` to find the right table or family, `describe_table` before `search_products`.
3. Search every grounded family/table; present up to 3-5 candidates with the exact model names and the specs that matter.
4. Explain trade-offs (field of view, distortion, working distance range, mount compatibility) and what could not be verified.
