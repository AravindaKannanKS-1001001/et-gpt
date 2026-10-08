"""
Build the site KB semantic index ("earth_tekniks") in shared Qdrant.

    uv run python -m et_mcp.services.site.index

Decoupled from server start; if skipped the server answers on BM25 alone.
"""
from __future__ import annotations

import logging
from pathlib import Path

from et_mcp.retrieval import Document, DocumentMetadata, build_index
from et_mcp.services.site.knowledge import CHUNKS, load_all

COLLECTION = "earth_tekniks"
META_FILE = Path(__file__).parent / "_index_meta.json"


def _documents() -> list[Document]:
    if not CHUNKS:
        load_all()
    return [
        Document(
            id=c.chunk_id,
            text=c.text,
            metadata=DocumentMetadata(
                source=c.doc_id, heading=c.heading, chunk_id=c.chunk_id,
                extra={"parent_id": c.doc_id, "heading": c.heading},
            ),
        )
        for c in CHUNKS.values()
    ]


def build() -> int:
    return build_index(COLLECTION, _documents(), meta_path=META_FILE)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    n = build()
    print(f"\n[ok] site index built: {n} chunks -> {COLLECTION!r}")
