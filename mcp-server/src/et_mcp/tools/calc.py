"""MCP tool layer for calc — thin wrappers over services.calc (no business logic here)."""
from __future__ import annotations

import re

from pydantic import ValidationError

from et_mcp.services.calc.dispatch import DISPATCH, run_calculation
from et_mcp.services.calc.knowledge_docs import DOCS
from et_mcp.services.calc.retrieval import search as _search


# calculate() accepts both ids; the knowledge doc exists only for the long one.
FORMULA_ALIASES = {"line_scan": "line_scan_frequency"}


def _lookup_key(key: str) -> str:
    """Spelling-insensitive key: '2/3"', '2/3 inch', '2/3-in' -> '2/3'; 'Full Frame' -> 'fullframe'."""
    k = re.sub(r'[\s"\u2033\u201d\u2019\'_-]', "", str(key).lower())
    return re.sub(r"(inches|inch|in)$", "", k)


def search_calculator(query: str, top_k: int = 10) -> dict:
    """Find optics calculators for a natural-language question. → get_calculator → calculate."""
    results = _search(query, top_k=int(top_k), has_tool=True)
    return {"results": [
        {"id": r.parent_id, "score": r.score, "category": r.category, "description": r.description}
        for r in results
    ]}


def get_calculator(formula_id: str) -> dict:
    """Get inputs, gotchas, related calculators for a formula_id. Call after search_calculator."""
    formula_id = FORMULA_ALIASES.get(formula_id, formula_id)
    doc = DOCS.get(formula_id)
    if not doc or doc.tool_name is None:
        available = sorted(k for k, d in DOCS.items() if d.tool_name is not None)
        return {"error": f"Unknown formula_id: {formula_id!r}", "available": available}
    entry = DISPATCH.get(formula_id)
    if not entry:
        return {"error": f"formula_id {formula_id!r} has no registered calculator"}
    input_model, _ = entry
    schema = input_model.model_json_schema()
    props = schema.get("properties", {})
    required_keys = schema.get("required", [])
    optional_keys = [k for k in props if k not in required_keys]
    meanings = doc.input_meanings
    return {
        "id": doc.id,
        "category": doc.category,
        "input_schema": schema,
        "required_inputs": [{"key": k, "meaning": meanings.get(k, "")} for k in required_keys],
        "optional_inputs": [{"key": k, "meaning": meanings.get(k, "")} for k in optional_keys],
        "gotchas": doc.gotchas,
        "related_calculators": doc.related,
        "chain_note": doc.chain_note,
    }


def calculate(formula_id: str, args: dict) -> dict:
    """Execute a calculator. Flow: search_calculator → get_calculator → calculate."""
    if formula_id not in DISPATCH:
        return {"valid": False, "error": f"Unknown formula_id {formula_id!r}", "available": sorted(DISPATCH.keys())}
    try:
        return run_calculation(formula_id, args or {})
    except ValidationError as e:
        missing = [str(err["loc"][0]) for err in e.errors() if err.get("type") in ("missing", "value_error.missing") and err.get("loc")]
        return {"valid": False, "missing": missing, "error": str(e)}
    except Exception as e:
        return {"valid": False, "error": str(e)}


def search_lookups(query: str, top_k: int = 10) -> dict:
    """Find reference/lookup tables (sensor sizes, f-stops, pixel formats). → get_reference → lookup."""
    results = _search(query, top_k=int(top_k), has_tool=False)
    return {"results": [
        {"id": r.parent_id, "score": r.score, "category": r.category, "description": r.description}
        for r in results
    ]}


def get_reference(table_id: str) -> dict:
    """Get a lookup table's purpose, keys, notes. Call after search_lookups."""
    doc = DOCS.get(table_id)
    if not doc or doc.tool_name is not None:
        available = sorted(k for k, d in DOCS.items() if d.tool_name is None)
        return {"error": f"Unknown table_id: {table_id!r}", "available": available}
    purpose = doc.chunks["purpose"].text if "purpose" in doc.chunks else ""
    available_keys = list(doc.lookup_table.keys()) if doc.lookup_table else []
    return {"id": doc.id, "category": doc.category, "purpose": purpose, "available_keys": available_keys, "notes": doc.notes, "gotchas": doc.gotchas, "common_uses": doc.common_uses}


def lookup(table_id: str, key: str) -> dict:
    """Retrieve one value from a reference table."""
    doc = DOCS.get(table_id)
    if not doc or doc.tool_name is not None:
        available = sorted(k for k, d in DOCS.items() if d.tool_name is None)
        return {"error": f"Unknown table_id: {table_id!r}", "available": available}
    if not doc.lookup_table:
        return {"error": f"Table {table_id!r} has no lookup data"}
    if key not in doc.lookup_table:
        matches = [k for k in doc.lookup_table if _lookup_key(k) == _lookup_key(key)]
        if len(matches) != 1:
            return {"valid": False, "error": f"Key {key!r} not found in {table_id!r}", "available_keys": list(doc.lookup_table.keys())}
        key = matches[0]
    return {"table_id": table_id, "key": key, "value": doc.lookup_table[key]}
