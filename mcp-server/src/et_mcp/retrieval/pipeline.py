"""
HybridPipeline — the shared semantic stage every server calls.

It owns ONLY vector recall (+ optional rerank). Cheap, server-specific keyword
stages (exact-id / tag index / BM25) stay in each server and fuse these scores
with their own (design/03; mirrors the battle-tested calculator fusion).

    keyword stages (per server) → HybridPipeline.search() → fuse / return
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field

from et_mcp.retrieval.embedder import Embedder
from et_mcp.retrieval.store import QdrantStore

logger = logging.getLogger(__name__)


@dataclass
class ScoredChunk:
    id: str
    text: str
    score: float                       # final score (rerank if reranked, else vector)
    vector_score: float = 0.0
    rerank_score: float | None = None
    metadata: dict = field(default_factory=dict)


class HybridPipeline:
    def __init__(self, vector_store: QdrantStore, embedder: Embedder,
                 reranker=None, enable_rerank: bool = False):
        self.vector_store = vector_store
        self.embedder = embedder
        self.reranker = reranker
        self.enable_rerank = enable_rerank and reranker is not None
        self._indexed: bool | None = None

    def _has_documents(self) -> bool:
        """True once the collection holds more than its metadata point.

        Until an index is built there is nothing to recall, so skip embedding
        (which would download the model) on every query.
        """
        if self._indexed is None:
            try:
                self._indexed = self.vector_store.count() > 1
            except Exception as exc:
                logger.warning("[pipeline] vector store unavailable — semantic stage skipped: %s", exc)
                self._indexed = False
        return self._indexed

    def search(self, query: str, top_k: int = 10, candidate_ids: set | None = None,
               oversample: int = 3) -> list[ScoredChunk]:
        """
        Semantic recall (+ optional rerank). Returns [] on any failure so a caller's
        keyword stages still answer (graceful degradation — never a hard crash).

        candidate_ids: keep only chunks whose parent/doc id is in the set.
        oversample:    pull top_k*oversample before reranking/truncating.
        """
        if not self._has_documents():
            return []
        try:
            qvec = self.embedder.embed_query(query)
        except Exception as exc:
            logger.warning("[pipeline] embedding failed — semantic stage skipped: %s", exc)
            return []

        try:
            raw = self.vector_store.search(qvec, top_k=max(top_k * oversample, top_k))
        except Exception as exc:
            logger.warning("[pipeline] vector search failed — semantic stage skipped: %s", exc)
            return []

        chunks: list[ScoredChunk] = []
        for r in raw:
            doc = r.document
            meta = dict(doc.metadata.extra or {})
            parent = meta.get("parent_id", doc.id)
            if candidate_ids is not None and parent not in candidate_ids and doc.id not in candidate_ids:
                continue
            chunks.append(ScoredChunk(
                id=doc.id, text=doc.text, score=r.score, vector_score=r.score,
                metadata={**meta, "heading": doc.metadata.heading, "source": doc.metadata.source},
            ))

        if self.enable_rerank and chunks:
            try:
                scores = self.reranker.rerank(query, [c.text for c in chunks])
                for c, s in zip(chunks, scores):
                    c.rerank_score = s
                    c.score = s
            except Exception as exc:
                logger.warning("[pipeline] rerank failed — using vector scores: %s", exc)

        chunks.sort(key=lambda c: c.score, reverse=True)
        return chunks[:top_k]
