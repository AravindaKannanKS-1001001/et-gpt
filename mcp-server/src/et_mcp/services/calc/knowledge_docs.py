"""
Knowledge store: load all markdown files, parse YAML frontmatter and section chunks.
Builds the tag inverted index, BM25 corpus, and ChromaDB semantic index used by retrieval.
"""

import json
import logging
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import yaml

logger = logging.getLogger(__name__)

KNOWLEDGE_DIR = Path(__file__).parent / "knowledge"


@dataclass
class KnowledgeChunk:
    chunk_id: str
    parent_id: str
    section: str
    text: str


@dataclass
class KnowledgeDoc:
    id: str
    category: str
    tags: list
    description: str
    required_inputs: list
    optional_inputs: list
    tool_name: Optional[str]
    chunks: dict               # section_name → KnowledgeChunk
    full_text: str
    related: list              # filled after all docs loaded
    input_meanings: dict       # key → meaning string (calculators only)
    gotchas: list              # list of strings
    chain_note: Optional[str]
    lookup_table: Optional[dict]   # reference docs only
    notes: Optional[dict]          # reference docs only
    common_uses: Optional[list]    # reference docs only


DOCS: dict = {}            # id → KnowledgeDoc
TAG_INDEX: dict = {}       # tag → [parent_id, ...]
BM25_DOCS: list = []       # ordered parent_ids
BM25_CORPUS: list = []     # ordered text strings (one per doc)


def _parse_frontmatter(content: str) -> tuple:
    if not content.startswith("---"):
        return {}, content
    try:
        end = content.index("---", 3)
    except ValueError:
        return {}, content
    raw_yaml = content[3:end].strip()
    meta = yaml.safe_load(raw_yaml) or {}
    body = content[end + 3:].strip()
    return meta, body


def _parse_sections(body: str) -> dict:
    sections = {}
    current = "overview"
    buf = []
    for line in body.splitlines():
        if line.startswith("# "):
            if buf:
                sections[current] = "\n".join(buf).strip()
            current = line[2:].strip().lower().replace(" ", "_")
            buf = []
        else:
            buf.append(line)
    if buf:
        sections[current] = "\n".join(buf).strip()
    return sections


def _extract_related_raw(sections: dict) -> list:
    """Pull snake_case identifiers from the Related Calculators section."""
    text = sections.get("related_calculators", "")
    return re.findall(r"\b([a-z][a-z0-9]*(?:_[a-z0-9]+)+)\b", text)


def _finalize_related() -> None:
    """After all docs loaded, filter related lists to valid doc IDs only."""
    known = set(DOCS.keys())
    for doc in DOCS.values():
        doc.related = [r for r in dict.fromkeys(doc.related) if r in known]


def _parse_input_meanings(text: str) -> dict:
    """Parse the Input Meanings section: key:\nmeaning text\n\nnext_key:\nmeaning..."""
    result = {}
    current_key = None
    buf = []
    for line in text.splitlines():
        m = re.match(r'^([a-z][a-z0-9_]*):\s*$', line.strip())
        if m:
            if current_key is not None:
                result[current_key] = " ".join(buf).strip()
            current_key = m.group(1)
            buf = []
        elif current_key is not None and line.strip():
            buf.append(line.strip())
    if current_key is not None:
        result[current_key] = " ".join(buf).strip()
    return result


def _parse_bullet_list(text: str) -> list:
    """Extract '- item' lines from a section as a list of strings."""
    items = []
    for line in text.splitlines():
        s = line.strip()
        if s.startswith("- "):
            items.append(s[2:].strip())
    return [i for i in items if i]


def _parse_json_lookup(text: str) -> Optional[dict]:
    """Extract the JSON code block from a # JSON Lookup section and return the inner dict."""
    m = re.search(r'```json\s*(\{.*?\})\s*```', text, re.DOTALL)
    if not m:
        return None
    try:
        obj = json.loads(m.group(1))
        # Strip the outer wrapper key (e.g. {"bytes_per_pixel": {...}}) → return inner dict
        if isinstance(obj, dict) and len(obj) == 1:
            return list(obj.values())[0]
        return obj
    except Exception:
        return None


def load_all() -> None:
    for md_path in KNOWLEDGE_DIR.rglob("*.md"):
        content = md_path.read_text(encoding="utf-8")
        meta, body = _parse_frontmatter(content)

        doc_id = meta.get("id") or md_path.stem
        category = meta.get("category", "unknown")
        tags = list(meta.get("tags") or [])
        description = meta.get("description", "")
        required_inputs = list(meta.get("required_inputs") or [])
        optional_inputs = list(meta.get("optional_inputs") or [])
        # Derive type from folder: calculators/ → has a runnable tool; reference/ → lookup table
        is_calculator = md_path.parent.name == "calculators"
        tool_name = doc_id if is_calculator else None
        chain_note = meta.get("chain_note") or None
        notes = meta.get("notes") or None
        common_uses_raw = meta.get("common_uses")
        common_uses = list(common_uses_raw) if common_uses_raw else None

        sections = _parse_sections(body)
        related_raw = _extract_related_raw(sections)

        input_meanings = _parse_input_meanings(sections.get("input_meanings", ""))
        gotchas = _parse_bullet_list(sections.get("gotchas", ""))
        lookup_table = _parse_json_lookup(sections.get("json_lookup", ""))

        chunks = {
            section: KnowledgeChunk(
                chunk_id=f"{doc_id}__{section}",
                parent_id=doc_id,
                section=section,
                text=text,
            )
            for section, text in sections.items()
        }

        # BM25 text: id + tags + description + purpose + example queries + use cases
        bm25_parts = [doc_id.replace("_", " ")]
        bm25_parts.extend(t.replace("_", " ") for t in tags)
        bm25_parts.append(description)
        bm25_parts.append(sections.get("purpose", ""))
        bm25_parts.append(sections.get("example_queries", ""))
        bm25_parts.append(sections.get("use_cases", ""))
        bm25_text = " ".join(bm25_parts)

        doc = KnowledgeDoc(
            id=doc_id,
            category=category,
            tags=tags,
            description=description,
            required_inputs=required_inputs,
            optional_inputs=optional_inputs,
            tool_name=tool_name,
            chunks=chunks,
            full_text=body,
            related=related_raw,
            input_meanings=input_meanings,
            gotchas=gotchas,
            chain_note=chain_note,
            lookup_table=lookup_table,
            notes=notes,
            common_uses=common_uses,
        )

        DOCS[doc_id] = doc
        BM25_DOCS.append(doc_id)
        BM25_CORPUS.append(bm25_text)

        for tag in tags:
            TAG_INDEX.setdefault(tag, []).append(doc_id)

    _finalize_related()


# Semantic indexing has moved OUT of import time. The cheap keyword layer below
# (markdown parse + tag index + BM25 corpus) is rebuilt at startup — it's fast and
# in-memory. The embedding/vector index now lives in a persistent shared Qdrant
# collection ("calculator_chunks"), built explicitly by `index.py` and queried in
# router/retrieval.py. This makes cold start fast and lets docs be re-indexed without
# restarting the server.
load_all()
