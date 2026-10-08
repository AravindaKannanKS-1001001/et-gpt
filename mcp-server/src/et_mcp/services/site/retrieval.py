"""
Site KB retrieval — BM25 + grep (keyword), no dense vector.

Stages (fused, confidence-gated):
  1. Exact doc_id match      (+100, rare but strong)
  2. Grep (token overlap)    (normalized 0-1, weight 0.4)
  3. BM25 over chunk text    (normalized 0-1, weight 0.6)

Dense vector (Qdrant) is OFF by design per user request — set DISABLE_SITE_VECTOR=true.
Keeps the service pure keyword, fast, no embedding download. BM25+grep alone is confident
when the top chunk covers >=50% of query tokens.
"""
from __future__ import annotations

import logging
import re
from collections import defaultdict
from dataclasses import dataclass

from rank_bm25 import BM25Okapi

from et_mcp.services.site.knowledge import BM25_CORPUS, BM25_IDS, CHUNKS, _tokenize, query_terms
from et_mcp.settings import settings

logger = logging.getLogger(__name__)

COLLECTION = "earth_tekniks"  # kept for name consistency, not used when vector disabled
MIN_CONFIDENCE_SCORE = settings.site_min_confidence
DISABLE_VECTOR = settings.disable_site_vector

# Weights when both stages fire — tuned for grep+BM25 (no semantic)
_GREP_WEIGHT = 0.4
_BM25_WEIGHT = 0.6

_bm25 = BM25Okapi(BM25_CORPUS) if BM25_CORPUS else None

# ── Lightweight grep inverted index (word -> chunk_ids) built once ──────────
_GREP_INDEX: dict[str, set[str]] = defaultdict(set)
for _cid, _chunk in CHUNKS.items():
    for _w in set(_tokenize(_chunk.text + " " + _chunk.heading)):
        if len(_w) >= 2:
            _GREP_INDEX[_w].add(_cid)


@dataclass
class Evidence:
    chunk_id: str
    doc_id: str
    heading: str
    text: str
    score: float


def _grep_scores(tokens: list[str], query_lower: str) -> dict[str, float]:
    """Token-overlap grep: +1 per matching token (exact word) + substring bonus, normalized 0-1."""
    if not tokens:
        return {}
    hit_counts: dict[str, int] = defaultdict(int)
    qset = set(tokens)
    # exact word hits via inverted index
    for tok in qset:
        for cid in _GREP_INDEX.get(tok, ()):
            hit_counts[cid] += 1
        # substring bonus (e.g. query 'vision' matches 'machine-vision')
        if len(tok) >= 4:
            for cid, chunk in CHUNKS.items():
                if tok in chunk.text.lower() and cid not in _GREP_INDEX.get(tok, ()):
                    hit_counts[cid] += 0.5
    if not hit_counts:
        return {}
    max_hits = max(hit_counts.values()) or 1.0
    # normalize to 0-1, also decay by query coverage so short queries don't over-score
    return {cid: min(1.0, cnt / max(len(qset), 1) * 1.2) for cid, cnt in hit_counts.items()}


def search(query: str, top_k: int = 5) -> tuple[list[Evidence], bool]:
    """Return (ranked evidence, confident?). No vector — BM25 + grep fused."""
    tokens = query_terms(query)
    query_lower = query.lower()
    if not tokens:
        return [], False

    # ── Stage 1: exact doc_id match (strong signal, rare) ───────────────
    exact_scores: dict[str, float] = {}
    for doc_id in {c.doc_id for c in CHUNKS.values()}:
        if doc_id in query_lower or doc_id.replace("_", " ") in query_lower:
            for cid, chunk in CHUNKS.items():
                if chunk.doc_id == doc_id:
                    exact_scores[cid] = 1.0

    # ── Stage 2: BM25 (normalized 0-1) ──────────────────────────────────
    bm25_scores: dict[str, float] = {}
    if _bm25 and tokens:
        raw = _bm25.get_scores(tokens)
        top = max(raw) if len(raw) and max(raw) > 0 else 1.0
        for cid, r in zip(BM25_IDS, raw):
            if r > 0:
                bm25_scores[cid] = float(r / top)

    # ── Stage 3: Grep token overlap (normalized 0-1) ─────────────────────
    grep_scores = _grep_scores(tokens, query_lower)
    # exact doc_id match dominates grep
    for cid, s in exact_scores.items():
        grep_scores[cid] = max(grep_scores.get(cid, 0.0), s)

    # ── Fuse (renormalized to stages that fired) ─────────────────────────
    bm25_used, grep_used = bool(bm25_scores), bool(grep_scores)
    if bm25_used and grep_used:
        wb, wg = _BM25_WEIGHT, _GREP_WEIGHT
    elif bm25_used:
        wb, wg = 1.0, 0.0
    elif grep_used:
        wb, wg = 0.0, 1.0
    else:
        return [], False

    scores: dict[str, float] = {}
    for cid in set(bm25_scores) | set(grep_scores):
        scores[cid] = wb * bm25_scores.get(cid, 0.0) + wg * grep_scores.get(cid, 0.0)

    ranked = sorted(scores.items(), key=lambda kv: kv[1], reverse=True)[:top_k]
    evidence = [
        Evidence(chunk_id=cid, doc_id=CHUNKS[cid].doc_id, heading=CHUNKS[cid].heading,
                 text=CHUNKS[cid].text, score=round(float(s), 4))
        for cid, s in ranked if cid in CHUNKS
    ]
    confident = _is_confident(evidence, tokens)
    return evidence, confident


def _is_confident(evidence: list[Evidence], tokens: list[str]) -> bool:
    """BM25+grep confidence: top chunk must cover >=50% of query terms (len>=3)."""
    if not evidence:
        return False
    top = evidence[0]
    # relative score gate tuned for BM25+grep (0.35 default)
    if top.score < MIN_CONFIDENCE_SCORE:
        return False
    q = {t for t in tokens if len(t) >= 3}
    if not q:
        return top.score >= 0.6
    covered = q & set(_tokenize(f"{top.doc_id.replace('_', ' ')} {top.heading} {top.text}"))
    return (len(covered) / len(q)) >= 0.5
