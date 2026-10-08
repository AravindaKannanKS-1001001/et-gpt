"""Core value types for the retrieval layer (framework-agnostic dataclasses)."""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class DocumentMetadata:
    source: str = ""          # parent document id
    heading: str = ""         # section name
    chunk_id: str = ""
    extra: dict = field(default_factory=dict)


@dataclass
class Document:
    id: str
    text: str
    metadata: DocumentMetadata = field(default_factory=DocumentMetadata)
    embedding: list[float] | None = None


@dataclass
class SearchResult:
    document: Document
    score: float               # cosine similarity in [0, 1]
