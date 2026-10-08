"""
Optional cross-encoder reranker (FastEmbed). Loaded lazily, once per process, and
only when a server opts in — so the ~200MB model isn't paid for unless used.

Kept as a final re-sort stage over a shortlist; off by default (design/03: rerank
is optional). Implemented via embedding cosine similarity to avoid a torch dep.
"""
from __future__ import annotations

import logging

from et_mcp.retrieval.config import RERANKER_MODEL_NAME

logger = logging.getLogger(__name__)


class CrossEncoderReranker:
    def __init__(self, model_name: str = RERANKER_MODEL_NAME):
        self.model_name = model_name
        self._model = None

    def is_loaded(self) -> bool:
        return self._model is not None

    def initialize(self) -> None:
        if self._model is None:
            logger.info("Loading reranker model %s ...", self.model_name)
            from fastembed import TextEmbedding

            self._model = TextEmbedding(model_name=self.model_name)
            logger.info("Reranker loaded.")

    def rerank(self, query: str, texts: list[str]) -> list[float]:
        """Return one relevance score per candidate text (higher = better)."""
        if not texts:
            return []
        if self._model is None:
            self.initialize()
        import numpy as np

        qv = np.array(list(self._model.embed([query]))[0], dtype=float)
        tvs = [np.array(v, dtype=float) for v in self._model.embed(texts)]
        qn = qv / (np.linalg.norm(qv) or 1.0)
        return [float(tv @ qn / (np.linalg.norm(tv) or 1.0)) for tv in tvs]
