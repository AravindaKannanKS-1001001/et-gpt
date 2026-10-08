"""Shared retrieval layer — one embedder, one Qdrant, one pipeline (design/03)."""
from et_mcp.retrieval.base import Document, DocumentMetadata, SearchResult
from et_mcp.retrieval.config import (
    EMBEDDING_DIM,
    EMBEDDING_MODEL_NAME,
    QDRANT_URL,
    RERANKER_MODEL_NAME,
)
from et_mcp.retrieval.embedder import Embedder
from et_mcp.retrieval.indexer import build_index, read_index_meta
from et_mcp.retrieval.pipeline import HybridPipeline, ScoredChunk
from et_mcp.retrieval.reranker import CrossEncoderReranker
from et_mcp.retrieval.store import QdrantStore, StoreMismatchError

__all__ = [
    "Document", "DocumentMetadata", "SearchResult",
    "EMBEDDING_DIM", "EMBEDDING_MODEL_NAME", "QDRANT_URL", "RERANKER_MODEL_NAME",
    "Embedder", "CrossEncoderReranker", "QdrantStore", "StoreMismatchError",
    "HybridPipeline", "ScoredChunk", "build_index", "read_index_meta",
]
