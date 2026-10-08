"""
Hybrid retrieval pipeline:
  Stage 1 — Exact ID match        (score +100)
  Stage 2 — Tag inverted index    (score +40 per matching tag)  ← exact grep, no embeddings
  Stage 3 — BM25 (rank-bm25)      (score 0-30 normalized)
  Stage 4 — Vector semantic       (score 0-20, shared Qdrant + bge-small-en-v1.5)

Stages 1-3 are unchanged. Stage 4 now queries a persistent shared Qdrant collection
("calculator_chunks") via the shared retrieval pipeline, instead of an in-memory
ChromaDB rebuilt on every start. Scores are still fused additively. The vector index
is built out-of-band by index.py — if it is missing/unreachable, Stage 4 is skipped
and the keyword stages still answer.
"""

import logging
import re
from dataclasses import dataclass
from typing import Optional

from rank_bm25 import BM25Okapi

from .knowledge_docs import BM25_CORPUS, BM25_DOCS, DOCS, TAG_INDEX
from et_mcp.settings import settings

logger = logging.getLogger(__name__)

# ── Shared semantic stage (lazy: connect to Qdrant + load embedder on first use) ──
COLLECTION = "calculator_chunks"
_pipeline = None
_pipeline_failed = False


def _get_pipeline():
    global _pipeline, _pipeline_failed
    if _pipeline is not None or _pipeline_failed:
        return _pipeline
    try:
        from et_mcp.retrieval import Embedder, HybridPipeline, QDRANT_URL, EMBEDDING_DIM, EMBEDDING_MODEL_NAME
        from et_mcp.retrieval import QdrantStore
        store = QdrantStore(url=QDRANT_URL, collection_name=COLLECTION,
                            vector_size=EMBEDDING_DIM, model_name=EMBEDDING_MODEL_NAME)
        store.initialize()
        # P1: vector recall only (no reranker — added in Phase 4). Fusion stays additive.
        _pipeline = HybridPipeline(store, Embedder(EMBEDDING_MODEL_NAME), reranker=None, enable_rerank=False)
        logger.info("[retrieval] semantic stage ready (Qdrant %s / %s)", QDRANT_URL, COLLECTION)
    except Exception as exc:
        logger.warning("[retrieval] semantic stage unavailable — keyword-only "
                       "(run `python index.py` and start Qdrant): %s", exc)
        _pipeline_failed = True
    return _pipeline


# ── Optional final-stage cross-encoder reranker (off by default; opt-in) ──────────
# Enable with ENABLE_RERANKING_CALC=true. Kept separate from site_knowledge's global
# ENABLE_RERANKING so turning it on there doesn't load a reranker in this process too
# (~200MB). When on, the top fused candidates are re-sorted by the cross-encoder.
_reranker = None
_reranker_failed = False


def _get_reranker():
    global _reranker, _reranker_failed
    if _reranker is not None or _reranker_failed:
        return _reranker
    if not settings.enable_reranking_calc:
        _reranker_failed = True
        return None
    try:
        from et_mcp.retrieval import CrossEncoderReranker, RERANKER_MODEL_NAME
        _reranker = CrossEncoderReranker(RERANKER_MODEL_NAME)
        logger.info("[retrieval] reranker enabled (%s)", RERANKER_MODEL_NAME)
    except Exception as exc:
        logger.warning("[retrieval] reranker unavailable: %s", exc)
        _reranker_failed = True
    return _reranker


def _apply_rerank(query: str, ranked: list, top_k: int) -> list:
    """Re-sort the fused shortlist with the cross-encoder (final stage). No-op if off."""
    rr = _get_reranker()
    if rr is None or not ranked:
        return ranked[:top_k]
    shortlist = ranked[: max(top_k * 2, top_k)]
    texts = [(DOCS[pid].description or DOCS[pid].full_text[:500]) for pid, _ in shortlist]
    try:
        rscores = rr.rerank(query, texts)
        order = sorted(range(len(shortlist)), key=lambda i: rscores[i], reverse=True)
        return [(shortlist[i][0], float(rscores[i])) for i in order][:top_k]
    except Exception as exc:
        logger.debug("[retrieval] rerank skipped: %s", exc)
        return ranked[:top_k]


@dataclass
class SearchResult:
    parent_id: str
    score: float
    category: str
    tool_name: Optional[str]
    description: str
    sections: list  # available section names


def _tokenize(text: str) -> list:
    return re.findall(r"\w+", text.lower())


# Build BM25 index once at import time
_bm25 = BM25Okapi([_tokenize(t) for t in BM25_CORPUS]) if BM25_CORPUS else None


def search(query: str, top_k: int = 10, category: Optional[str] = None, has_tool: Optional[bool] = None) -> list:
    scores: dict = {}
    tokens = _tokenize(query)
    query_lower = query.lower()
    query_words = set(tokens)

    # Stage 1: Exact ID match (+100)
    for doc_id in DOCS:
        if doc_id in query_lower or doc_id.replace("_", " ") in query_lower:
            scores[doc_id] = scores.get(doc_id, 0.0) + 100.0

    # Stage 2: Tag inverted index — exact grep, no embeddings (+40 per hit)
    for tag, doc_ids in TAG_INDEX.items():
        tag_words = set(tag.lower().replace("_", " ").split())
        if tag_words & query_words or tag.lower() in query_lower:
            for doc_id in doc_ids:
                scores[doc_id] = scores.get(doc_id, 0.0) + 40.0

    # Stage 3: BM25 (0-30 normalized)
    if _bm25 and tokens:
        raw = _bm25.get_scores(tokens)
        max_raw = max(raw) if max(raw) > 0 else 1.0
        for i, doc_id in enumerate(BM25_DOCS):
            normalized = (raw[i] / max_raw) * 30.0
            scores[doc_id] = scores.get(doc_id, 0.0) + normalized

    # Stage 4: Vector semantic search via shared Qdrant pipeline (0-20, cosine similarity)
    pipe = _get_pipeline()
    if pipe is not None:
        try:
            sem_by_parent: dict = {}
            for ch in pipe.search(query, top_k=top_k * 3):
                parent_id = ch.metadata.get("parent_id")
                if not parent_id:
                    continue
                # vector_score is cosine similarity in [0,1] → map to [0,20];
                # keep the best-scoring chunk per parent (no double-counting).
                sscore = max(0.0, min(ch.vector_score, 1.0)) * 20.0
                sem_by_parent[parent_id] = max(sem_by_parent.get(parent_id, 0.0), sscore)
            for parent_id, sscore in sem_by_parent.items():
                scores[parent_id] = scores.get(parent_id, 0.0) + sscore
        except Exception as exc:
            logger.debug(f"[retrieval] semantic search skipped: {exc}")

    # Filter by category if requested
    if category:
        scores = {k: v for k, v in scores.items() if DOCS[k].category == category}

    # Filter by whether the doc has a runnable tool_name
    if has_tool is not None:
        scores = {k: v for k, v in scores.items() if (DOCS[k].tool_name is not None) == has_tool}

    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    ranked = _apply_rerank(query, ranked, top_k)  # opt-in final stage (off by default)

    results = []
    for doc_id, score in ranked:
        doc = DOCS[doc_id]
        results.append(SearchResult(
            parent_id=doc_id,
            score=round(score, 2),
            category=doc.category,
            tool_name=doc.tool_name,
            description=doc.description,
            sections=list(doc.chunks.keys()),
        ))
    return results
