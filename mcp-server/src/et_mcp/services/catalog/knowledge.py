"""
etk_mcp/knowledge.py
═════════════════════════════════════════════════════════════════════════════════
RAG knowledge layer for the lens catalog — the agentic "search → get knowledge"
flow (mirrors the calculator MCP's search_calculator → get_calculator).

The rich domain knowledge lives in docs/*.md (per-table Purpose, Attributes with
column meanings, Example NL→SQL queries, Relationships, Notes/gotchas). This module
parses those once into structured knowledge and exposes:

  search(query, top_k)   — use-case / NL question → ranked relevant tables, via a
                           dependency-free BM25 over each table's doc. Answers
                           "which lens family/table do I use for X?".
  get_knowledge(table)   — the full knowledge doc for a table: purpose, column
                           meanings, example queries, gotchas, relationships.
                           Answers "what is this table, when to use it, how to query it".

No ChromaDB / no Ollama — deterministic and agnostic. (The vector-RAG pipeline is
still available separately via the optional query_catalog tool.)
═════════════════════════════════════════════════════════════════════════════════
"""
import glob
import math
import os
import re

from .generate_chunks import PRODUCT_TYPE_REGISTRY
from et_mcp.settings import settings

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_DOCS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "docs")


# ── Parsing docs/*.md into per-table knowledge ──────────────────────────────────

def _split_sections(block: str) -> dict:
    """Split a table block into its ## sections."""
    parts = re.split(r"\n##\s+", "\n" + block)
    sections = {}
    for p in parts[1:]:
        head, _, body = p.partition("\n")
        sections[head.strip().lower()] = body.strip()
    return sections


def _parse_attributes(attr_md: str) -> list:
    """Parse the '| Column | Meaning | Datatype | Notes |' table into structured rows."""
    cols = []
    for line in attr_md.splitlines():
        line = line.strip()
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if len(cells) < 2:
            continue
        if cells[0].lower() in ("column", "") or set(cells[0]) <= {"-", ":"}:
            continue  # header / separator
        cols.append({
            "name": cells[0],
            "meaning": cells[1] if len(cells) > 1 else "",
            "datatype": cells[2] if len(cells) > 2 else "",
            "notes": cells[3] if len(cells) > 3 else "",
        })
    return cols


def _parse_examples(ex_md: str) -> list:
    """Extract {question, sql} pairs from an Example Queries section."""
    examples = []
    # Each example: a 'Natural Language:' line (or bold title) followed by a ```sql block.
    sql_blocks = list(re.finditer(r"```sql\s*(.*?)\s*```", ex_md, re.DOTALL | re.IGNORECASE))
    for m in sql_blocks:
        sql = m.group(1).strip()
        before = ex_md[:m.start()]
        nl = ""
        nlm = list(re.finditer(r"Natural Language:\s*\n+(.+)", before))
        if nlm:
            nl = nlm[-1].group(1).strip().splitlines()[0].strip()
        examples.append({"question": nl, "sql": sql})
    return examples


def _load_knowledge() -> dict:
    """table_name → structured knowledge dict."""
    kb = {}
    for md in sorted(glob.glob(os.path.join(_DOCS, "*.md"))):
        content = open(md, encoding="utf-8").read()
        for block in re.split(r"\n#\s*Table:\s*", "\n" + content)[1:]:
            table = block.split("\n", 1)[0].strip()
            if not table or table in kb:
                continue
            sec = _split_sections(block)
            kb[table] = {
                "table": table,
                "family": PRODUCT_TYPE_REGISTRY.get(table, "unknown"),
                "purpose": sec.get("purpose", "").strip(),
                "columns": _parse_attributes(sec.get("attributes", "")),
                "example_queries": _parse_examples(sec.get("example queries", "")),
                "relationships": sec.get("relationships", "").strip(),
                "gotchas": sec.get("notes", "").strip(),
            }
    return kb


KB = _load_knowledge()


# ── Dependency-free BM25 over the per-table docs ────────────────────────────────

_TOKEN_RE = re.compile(r"[a-z0-9]+")


def _tokenize(text: str) -> list:
    return _TOKEN_RE.findall(text.lower())


def _doc_text(entry: dict) -> str:
    """Searchable text for a table: purpose + column meanings + example questions
    + family. Purpose carries the application/use-case keywords."""
    cols = " ".join(f"{c['name']} {c['meaning']}" for c in entry["columns"])
    qs = " ".join(e["question"] for e in entry["example_queries"])
    return f"{entry['family']} {entry['purpose']} {cols} {qs}"


_TABLES = list(KB.keys())
_DOC_TOKENS = {t: _tokenize(_doc_text(KB[t])) for t in _TABLES}
_DOC_LEN = {t: len(toks) for t, toks in _DOC_TOKENS.items()}
_AVGDL = (sum(_DOC_LEN.values()) / len(_DOC_LEN)) if _DOC_LEN else 0.0
_DF = {}
for _toks in _DOC_TOKENS.values():
    for _term in set(_toks):
        _DF[_term] = _DF.get(_term, 0) + 1
_N = len(_TABLES)

_K1, _B = 1.5, 0.75


# ── Shared semantic stage (lazy: Qdrant + bge-small-en-v1.5) ─────────────────────
# One vector per table doc (same unit as the BM25 layer) → semantic table routing.
# Built out-of-band by index.py into the shared "catalog_knowledge" collection.
COLLECTION = "catalog_knowledge"
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
        _pipeline = HybridPipeline(store, Embedder(EMBEDDING_MODEL_NAME), reranker=None, enable_rerank=False)
    except Exception:
        _pipeline_failed = True
    return _pipeline


def _semantic_scores(query: str, top_k: int) -> dict:
    """table → cosine similarity (0..1) from the shared vector index. {} if unavailable."""
    pipe = _get_pipeline()
    if pipe is None:
        return {}
    try:
        out = {}
        for ch in pipe.search(query, top_k=max(top_k * 3, top_k)):
            table = ch.metadata.get("parent_id") or ch.id
            out[table] = max(out.get(table, 0.0), max(0.0, min(ch.vector_score, 1.0)))
        return out
    except Exception:
        return {}


def _bm25_scores(query: str) -> dict:
    """table → raw BM25 score (>0 only). BM25 math is unchanged."""
    q_terms = _tokenize(query)
    out = {}
    for t in _TABLES:
        toks = _DOC_TOKENS[t]
        if not toks:
            continue
        tf = {}
        for term in toks:
            tf[term] = tf.get(term, 0) + 1
        dl = _DOC_LEN[t]
        score = 0.0
        for term in q_terms:
            if term not in tf:
                continue
            idf = math.log(1 + (_N - _DF[term] + 0.5) / (_DF[term] + 0.5))
            freq = tf[term]
            score += idf * (freq * (_K1 + 1)) / (freq + _K1 * (1 - _B + _B * dl / _AVGDL))
        if score > 0:
            out[t] = score
    return out


# ── Optional final-stage cross-encoder reranker (off by default; opt-in) ──────────
# Enable with ENABLE_RERANKING_CATALOG=true. Separate from site_knowledge's global
# ENABLE_RERANKING so it doesn't load a reranker in this process (~200MB) unless asked.
_reranker = None
_reranker_failed = False


def _get_reranker():
    global _reranker, _reranker_failed
    if _reranker is not None or _reranker_failed:
        return _reranker
    if not settings.enable_reranking_catalog:
        _reranker_failed = True
        return None
    try:
        from et_mcp.retrieval import CrossEncoderReranker, RERANKER_MODEL_NAME
        _reranker = CrossEncoderReranker(RERANKER_MODEL_NAME)
    except Exception:
        _reranker_failed = True
    return _reranker


def _apply_rerank(query: str, ranked: list, top_k: int) -> list:
    """Re-sort the fused table shortlist with the cross-encoder. No-op if off."""
    rr = _get_reranker()
    if rr is None or not ranked:
        return ranked[:top_k]
    shortlist = ranked[: max(top_k * 2, top_k)]
    texts = [_doc_text(KB[t]) for t, _ in shortlist]
    try:
        rscores = rr.rerank(query, texts)
        order = sorted(range(len(shortlist)), key=lambda i: rscores[i], reverse=True)
        return [(shortlist[i][0], float(rscores[i])) for i in order][:top_k]
    except Exception:
        return ranked[:top_k]


def search(query: str, top_k: int = 10) -> dict:
    """Rank tables for a NL query: BM25 (keyword) fused with shared semantic recall.

    Same return shape as before. When the vector index is unavailable, this is pure
    BM25 (identical to the previous behaviour). When available, a paraphrase like
    "lenses for dark environments" can surface the low-light table even if BM25 misses
    the exact keyword.
    """
    bm25 = _bm25_scores(query)
    sem = _semantic_scores(query, top_k)

    if sem:
        bmax = max(bm25.values()) if bm25 else 1.0
        fused = {}
        for t in set(bm25) | set(sem):
            b = (bm25.get(t, 0.0) / bmax) if bmax else 0.0   # normalise BM25 to [0,1]
            fused[t] = 0.5 * b + 0.5 * sem.get(t, 0.0)        # equal-weight blend
        ranked = sorted(fused.items(), key=lambda x: x[1], reverse=True)
    else:
        ranked = sorted(bm25.items(), key=lambda x: x[1], reverse=True)

    ranked = _apply_rerank(query, ranked, top_k)  # opt-in final stage (off by default)

    results = []
    for t, score in ranked:
        e = KB[t]
        purpose = re.split(r"(?<=\.)\s", e["purpose"].replace("**", ""))[0] if e["purpose"] else ""
        results.append({
            "table": t,
            "family": e["family"],
            "score": round(float(score), 3),
            "purpose": purpose[:240],
        })
    return {"query": query, "results": results}


def get_knowledge(table: str) -> dict:
    """Full knowledge doc for a table: purpose, column meanings, example NL→SQL
    queries, gotchas, and relationships."""
    e = KB.get(table)
    if not e:
        return {"error": f"No knowledge doc for table '{table}'. "
                         f"Use search_knowledge() or list_tables() for valid names."}
    return e
