"""Tool registry — maps server names to MCP tool callables (no ADK, no orchestrator)."""
from __future__ import annotations

from et_mcp.tools import calc as calc_mod
from et_mcp.tools import catalog as catalog_mod
from et_mcp.tools import site as site_mod

TOOLSETS: dict[str, dict[str, callable]] = {
    "calc": {
        "search_calculator": calc_mod.search_calculator,
        "get_calculator": calc_mod.get_calculator,
        "calculate": calc_mod.calculate,
        "search_lookups": calc_mod.search_lookups,
        "get_reference": calc_mod.get_reference,
        "lookup": calc_mod.lookup,
    },
    "site": {
        "search_knowledge_base": site_mod.search_knowledge_base,
        "get_document": site_mod.get_document,
    },
    "catalog": {
        "list_families": catalog_mod.list_families,
        "list_tables": catalog_mod.list_tables,
        "describe_table": catalog_mod.describe_table,
        "search_knowledge": catalog_mod.search_knowledge,
        "get_table_knowledge": catalog_mod.get_table_knowledge,
        "lookup_model": catalog_mod.lookup_model,
        "get_product": catalog_mod.get_product,
        "search_products": catalog_mod.search_products,
        "run_select": catalog_mod.run_select,
    },
}

ALL_TOOLS: dict[str, callable] = {name: fn for tools in TOOLSETS.values() for name, fn in tools.items()}


def tools_for(server_names: list[str]) -> dict[str, callable]:
    """Return flattened {tool_name: callable} for given server names."""
    out: dict[str, callable] = {}
    for name in server_names:
        out.update(TOOLSETS.get(name, {}))
    return out
