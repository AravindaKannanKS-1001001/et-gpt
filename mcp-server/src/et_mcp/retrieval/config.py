"""Shared retrieval config — standalone, reads from settings (no _PROJECT_ROOT leak)."""
from __future__ import annotations

from et_mcp.settings import settings

EMBEDDING_MODEL_NAME: str = settings.embedding_model_name
EMBEDDING_DIM: int = settings.embedding_dim
RERANKER_MODEL_NAME: str = settings.reranker_model_name
QDRANT_URL: str = settings.resolved_qdrant_url
