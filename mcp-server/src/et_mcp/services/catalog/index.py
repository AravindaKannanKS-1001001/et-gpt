"""
Build the catalog's semantic table-routing index ("catalog_knowledge") in Qdrant.

One vector per table doc (same unit as the BM25 layer in knowledge.py), so
search_knowledge can route use-case queries to the right table. The DB itself is
NOT embedded — data access hits Supabase directly.

    uv run python -m et_mcp.services.catalog.index
"""
from __future__ import annotations

import logging
from pathlib import Path

from et_mcp.retrieval import Document, DocumentMetadata, build_index
from et_mcp.services.catalog import knowledge

COLLECTION = "catalog_knowledge"
META_FILE = Path(__file__).parent / "_index_meta.json"


def _documents() -> list[Document]:
    docs: list[Document] = []
    for table, entry in knowledge.KB.items():
        text = knowledge._doc_text(entry).strip()
        if not text:
            continue
        docs.append(Document(
            id=table,
            text=text,
            metadata=DocumentMetadata(
                source=table, heading=entry.get("family", ""), chunk_id=table,
                extra={"parent_id": table, "family": entry.get("family", "")},
            ),
        ))
    return docs


def build() -> int:
    return build_index(COLLECTION, _documents(), meta_path=META_FILE)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    n = build()
    print(f"\n[ok] catalog index built: {n} table docs -> {COLLECTION!r}")
