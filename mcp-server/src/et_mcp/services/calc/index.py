"""
Build the calculator's semantic index ("calculator_chunks") in shared Qdrant.

Decoupled from server start — run explicitly when knowledge docs change (or via the
watchdog). If skipped/unreachable, the calculator still answers on its keyword
stages (exact-id / tag index / BM25).

    uv run python -m et_mcp.services.calc.index
"""
from __future__ import annotations

import logging
from pathlib import Path

from et_mcp.retrieval import Document, DocumentMetadata, build_index
from et_mcp.services.calc.knowledge_docs import DOCS, load_all

COLLECTION = "calculator_chunks"
META_FILE = Path(__file__).parent / "_index_meta.json"


def _documents() -> list[Document]:
    if not DOCS:
        load_all()
    docs: list[Document] = []
    for doc in DOCS.values():
        for section, chunk in doc.chunks.items():
            text = chunk.text.strip()
            if not text:
                continue
            docs.append(Document(
                id=chunk.chunk_id,
                text=text,
                metadata=DocumentMetadata(
                    source=doc.id, heading=section, chunk_id=chunk.chunk_id,
                    extra={"parent_id": doc.id, "section": section,
                           "category": doc.category, "has_tool": doc.tool_name is not None},
                ),
            ))
    return docs


def build() -> int:
    return build_index(COLLECTION, _documents(), meta_path=META_FILE)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    n = build()
    print(f"\n[ok] calculator index built: {n} chunks -> {COLLECTION!r}")
