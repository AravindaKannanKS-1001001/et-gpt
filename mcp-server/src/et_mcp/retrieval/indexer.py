"""
Generic index builder — embed a list of Documents and (re)load a Qdrant collection.

Indexing is decoupled from server start (old.md §8 "decoupled indexing"): each
server calls this explicitly (via its own index entrypoint or the watchdog), and
if the index is missing the server still answers on its keyword stages.
"""
from __future__ import annotations

import json
import logging
import time
from pathlib import Path

from et_mcp.retrieval.base import Document
from et_mcp.retrieval.config import EMBEDDING_DIM, EMBEDDING_MODEL_NAME, QDRANT_URL
from et_mcp.retrieval.embedder import Embedder
from et_mcp.retrieval.store import QdrantStore

logger = logging.getLogger(__name__)


def build_index(
    collection: str,
    documents: list[Document],
    *,
    url: str = QDRANT_URL,
    embedder: Embedder | None = None,
    meta_path: Path | None = None,
) -> int:
    """Embed `documents` and rebuild `collection`. Returns the chunk count."""
    if not documents:
        raise RuntimeError(f"No documents to index for collection {collection!r}.")

    embedder = embedder or Embedder(EMBEDDING_MODEL_NAME)
    embedder.initialize()
    logger.info("Embedding %d chunks with %s ...", len(documents), embedder.model_name)
    vectors = embedder.embed_texts([d.text for d in documents])
    for d, v in zip(documents, vectors):
        d.embedding = v

    store = QdrantStore(url=url, collection_name=collection,
                        vector_size=EMBEDDING_DIM, model_name=embedder.model_name)
    store.initialize()
    store.reset()
    store.add_documents(documents)
    store.close()  # release the client (matters for local-path mode; harmless for HTTP)

    if meta_path is not None:
        meta_path.write_text(json.dumps({
            "built_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
            "chunk_count": len(documents),
            "model": embedder.model_name,
            "collection": collection,
            "qdrant_url": url,
        }, indent=2), encoding="utf-8")

    logger.info("Indexed %d chunks into %r at %s", len(documents), collection, url)
    return len(documents)


def read_index_meta(meta_path: Path) -> dict:
    if meta_path.exists():
        try:
            return json.loads(meta_path.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}
