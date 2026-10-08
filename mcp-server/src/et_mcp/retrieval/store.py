"""
Qdrant-backed vector store. Supports HTTP (shared), local path, and :memory: modes.

A single metadata point stamps the collection with the embedding model + dim so a
mismatch is caught loudly (design convention: explicit failure states) rather than
silently returning garbage from an incompatible index.
"""
from __future__ import annotations

import logging
import uuid

from et_mcp.retrieval.base import Document, DocumentMetadata, SearchResult

logger = logging.getLogger(__name__)

_METADATA_ID = str(uuid.uuid5(uuid.NAMESPACE_URL, "COLLECTION_METADATA"))

# Local-path Qdrant takes an exclusive file lock, so every store in this process
# (calc + catalog under --server all) must share one client per location.
_SHARED_CLIENTS: dict[str, object] = {}


def _client_for(url: str):
    from qdrant_client import QdrantClient

    from et_mcp.settings import settings

    if url == ":memory:":
        return QdrantClient(location=":memory:")
    if url not in _SHARED_CLIENTS:
        if url.startswith("http"):
            key = settings.qdrant_api_key.get_secret_value() if settings.qdrant_api_key else None
            _SHARED_CLIENTS[url] = QdrantClient(url=url, api_key=key)
        else:
            _SHARED_CLIENTS[url] = QdrantClient(path=url)
    return _SHARED_CLIENTS[url]


class StoreMismatchError(RuntimeError):
    """The live collection was built with an incompatible model/dimension."""


class QdrantStore:
    def __init__(self, url: str, collection_name: str, vector_size: int, model_name: str):
        self.url = url
        self.collection_name = collection_name
        self.vector_size = vector_size
        self.model_name = model_name
        self._client = None

    # ── lifecycle ──────────────────────────────────────────────────────────────
    def initialize(self) -> None:
        if self._client is not None:
            return
        self._client = _client_for(self.url)

        if not self._client.collection_exists(self.collection_name):
            self._create_collection()
        else:
            self._verify_metadata()

    def _create_collection(self) -> None:
        from qdrant_client.models import Distance, PointStruct, VectorParams

        self._client.create_collection(
            collection_name=self.collection_name,
            vectors_config=VectorParams(size=self.vector_size, distance=Distance.COSINE),
        )
        self._client.upsert(
            collection_name=self.collection_name,
            points=[PointStruct(
                id=_METADATA_ID,
                vector=[0.0] * self.vector_size,
                payload={"is_metadata": True, "model_name": self.model_name,
                         "vector_size": self.vector_size},
            )],
        )
        logger.info("Created Qdrant collection %s", self.collection_name)

    def _verify_metadata(self) -> None:
        points = self._client.retrieve(collection_name=self.collection_name, ids=[_METADATA_ID])
        if not points:
            return
        payload = points[0].payload or {}
        if payload.get("vector_size") and payload["vector_size"] != self.vector_size:
            raise StoreMismatchError(
                f"{self.collection_name}: collection dim {payload['vector_size']} "
                f"!= app dim {self.vector_size}"
            )
        if payload.get("model_name") and payload["model_name"] != self.model_name:
            logger.warning("%s: collection built with %r but running %r",
                           self.collection_name, payload["model_name"], self.model_name)

    def close(self) -> None:
        if self._client and self.url == ":memory:":
            self._client.close()
        self._client = None  # shared clients stay open for the other stores

    # ── read ───────────────────────────────────────────────────────────────────
    def search(self, query_embedding: list[float], top_k: int = 5) -> list[SearchResult]:
        if not self._client:
            self.initialize()
        hits = self._client.query_points(
            collection_name=self.collection_name, query=query_embedding, limit=top_k
        ).points
        results: list[SearchResult] = []
        for hit in hits:
            meta = hit.payload or {}
            if meta.get("is_metadata"):
                continue
            score = max(0.0, min(float(hit.score), 1.0))
            doc = Document(
                id=meta.get("id", str(hit.id)),
                text=meta.get("text", ""),
                metadata=DocumentMetadata(
                    source=meta.get("source", ""),
                    heading=meta.get("heading", ""),
                    chunk_id=meta.get("chunk_id", str(hit.id)),
                    extra=meta.get("extra", {}),
                ),
            )
            results.append(SearchResult(document=doc, score=score))
        return results

    def count(self) -> int:
        if not self._client:
            self.initialize()
        return self._client.get_collection(self.collection_name).points_count or 0

    def health(self) -> bool:
        try:
            if not self._client:
                self.initialize()
            self._client.get_collections()
            return True
        except Exception as exc:
            logger.warning("Qdrant health check failed: %s", exc)
            return False

    # ── write ──────────────────────────────────────────────────────────────────
    def add_documents(self, documents: list[Document]) -> None:
        if not self._client:
            self.initialize()
        from qdrant_client.models import PointStruct

        points = []
        for doc in documents:
            if doc.embedding is None:
                raise ValueError(f"Document {doc.id} is missing an embedding.")
            points.append(PointStruct(
                id=str(uuid.uuid5(uuid.NAMESPACE_URL, doc.id)),
                vector=doc.embedding,
                payload={
                    "id": doc.id, "text": doc.text,
                    "source": doc.metadata.source, "heading": doc.metadata.heading,
                    "chunk_id": doc.metadata.chunk_id, "extra": doc.metadata.extra or {},
                },
            ))
        self._client.upsert(collection_name=self.collection_name, points=points)
        logger.info("Upserted %d documents into %s", len(documents), self.collection_name)

    def reset(self) -> None:
        if not self._client:
            self.initialize()
        if self._client.collection_exists(self.collection_name):
            self._client.delete_collection(self.collection_name)
        self._create_collection()
