"""MCP tool layer for site knowledge — thin wrappers over services.site."""
from __future__ import annotations

from et_mcp.services.site.knowledge import DOCS
from et_mcp.services.site.retrieval import search as _search


def search_knowledge_base(query: str, top_k: int = 5) -> dict:
    """Search EarthTekniks KB (company, platforms, projects, vision fundamentals). Returns ranked snippets + confident flag."""
    query = (query or "").strip()
    if not query:
        return {"error": "query cannot be empty"}
    top_k = max(1, min(int(top_k), 15))
    evidence, confident = _search(query, top_k=top_k)
    return {
        "confident": confident,
        "note": None if confident else "No high-confidence match — do not answer from memory.",
        "results": [{"doc_id": e.doc_id, "heading": e.heading, "score": e.score, "snippet": e.text[:600]} for e in evidence],
    }


def get_document(doc_id: str) -> dict:
    """Read full text of a KB document by doc_id."""
    doc = DOCS.get(doc_id)
    if doc is None:
        return {"error": f"Unknown doc_id {doc_id!r}", "available": sorted(DOCS)}
    return {"doc_id": doc.doc_id, "title": doc.title, "text": doc.text}
