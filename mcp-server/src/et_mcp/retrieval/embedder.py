"""
Embedding service — FastEmbed (ONNX, no torch/CUDA). One instance per process.

Design/03: exactly one embedder definition shared by every server, so all
collections are built and queried with the same model.
"""
from __future__ import annotations

import logging

from et_mcp.retrieval.config import EMBEDDING_MODEL_NAME

logger = logging.getLogger(__name__)


class Embedder:
    def __init__(self, model_name: str = EMBEDDING_MODEL_NAME):
        self.model_name = model_name
        self._model = None

    def is_loaded(self) -> bool:
        return self._model is not None

    def initialize(self) -> None:
        if self._model is None:
            logger.info("Loading embedding model %s ...", self.model_name)
            from fastembed import TextEmbedding

            self._model = TextEmbedding(model_name=self.model_name)
            logger.info("Embedding model loaded.")

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        """Embed DOCUMENTS/passages (used at index time)."""
        if self._model is None:
            self.initialize()
        # bge and similar are asymmetric: passages get no instruction prefix.
        embed = getattr(self._model, "passage_embed", self._model.embed)
        return [list(v) for v in embed(texts)]

    def embed_query(self, text: str) -> list[float]:
        """Embed a QUERY. Asymmetric models prepend a search instruction here,
        which sharply improves relevant/irrelevant separation (bge)."""
        if self._model is None:
            self.initialize()
        query_embed = getattr(self._model, "query_embed", None)
        if query_embed is not None:
            return list(list(query_embed([text]))[0])
        return list(list(self._model.embed([text]))[0])
