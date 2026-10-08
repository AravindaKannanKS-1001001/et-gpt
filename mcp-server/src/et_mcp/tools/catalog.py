"""MCP tool layer for catalog — thin wrappers over services.catalog."""
from __future__ import annotations

from et_mcp.services.catalog import indexes, knowledge, query


def _db_guarded(fn, *args) -> dict:
    try:
        return fn(*args)
    except Exception as e:
        return {"error": f"{type(e).__name__}: {e}", "hint": "Catalog DB unavailable — check SUPABASE_DB_URL in .env."}


def list_families() -> dict:
    """List lens families and their tables."""
    return indexes.list_families()


def list_tables(family: str | None = None) -> dict:
    """List catalog tables with purpose. Optional family filter."""
    return indexes.list_tables(family)


def describe_table(table: str) -> dict:
    """Describe a table: columns, purpose, signature columns. Call before run_select."""
    return indexes.describe_table(table)


def search_knowledge(query: str, top_k: int = 10) -> dict:
    """Find which table/family fits a use-case NL question. → get_table_knowledge."""
    return knowledge.search(query, int(top_k))


def get_table_knowledge(table: str) -> dict:
    """Full knowledge for a table: purpose, column meanings, NL->SQL examples, gotchas."""
    return knowledge.get_knowledge(table)


def lookup_model(name: str) -> dict:
    """Find which table/family a lens model belongs to."""
    return indexes.find_model(name)


def get_product(model_name: str) -> dict:
    """Get full spec row(s) for a lens model."""
    return _db_guarded(query.get_product, model_name)


def search_products(table: str | None = None, family: str | None = None, filters: list | None = None, columns: list | None = None, sort: dict | None = None, limit: int = 50) -> dict:
    """Filtered search over one table or family. filters: [{column, op, value}]."""
    return _db_guarded(query.search_products, table, family, filters, columns, sort, int(limit))


def run_select(sql: str) -> dict:
    """Run a validated read-only SELECT."""
    return _db_guarded(query.run_select, sql)
