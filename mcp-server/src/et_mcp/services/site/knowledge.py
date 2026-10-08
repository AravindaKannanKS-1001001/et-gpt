"""
Company knowledge base — load + chunk the docs, build the in-memory keyword layer.

Thin rebuild (design/03 three-verb; old.md §8 shared-retrieval + confidence gating):
the elaborate classifier/router/entity machinery from the old site_knowledge
server is intentionally dropped. What remains is the useful core — the docs, a
size-based chunker, and a BM25 corpus — feeding the shared HybridPipeline.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

DOCS_DIR = Path(__file__).parent / "docs"

CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200
MIN_CHUNK_CHARS = 200


@dataclass
class Chunk:
    chunk_id: str
    doc_id: str
    heading: str
    text: str


@dataclass
class KBDoc:
    doc_id: str
    title: str
    text: str


DOCS: dict[str, KBDoc] = {}          # doc_id -> KBDoc (full text, for get_document)
CHUNKS: dict[str, Chunk] = {}        # chunk_id -> Chunk
BM25_IDS: list[str] = []             # ordered chunk_ids
BM25_CORPUS: list[list[str]] = []    # tokenized chunk texts


# Function words carry no retrieval signal but would otherwise dominate the
# grep overlap score and the confidence coverage check.
STOPWORDS = frozenset("""a an and are as at be by can could do does did for from has have how i if in
is it its me my of on or our please should so tell that the their them there these this to us
was we what when where which who why will with would you your about any all also""".split())


def _tokenize(text: str) -> list[str]:
    # Customers write "EarthTekniks"; the documents say "Earth Tekniks".
    text = re.sub(r"earth[\s-]*tekniks", "earthtekniks", text.lower())
    # Fold simple plurals so "bottle" matches "bottles".
    return [t[:-1] if len(t) > 3 and t.endswith("s") and not t.endswith("ss") else t
            for t in re.findall(r"\w+", text)]


def query_terms(text: str) -> list[str]:
    """Query tokens without stopwords (falls back to all tokens if nothing remains)."""
    tokens = _tokenize(text)
    return [t for t in tokens if t not in STOPWORDS] or tokens


def _split_sections(body: str) -> list[tuple[str, str]]:
    """Split markdown into (heading path, text) by '#' headings; keep order.

    The heading includes its parent sections below the document title, e.g.
    "Office Information > Address", so a parent heading without its own body
    (like "Office Information") still makes its subsections searchable.
    """
    sections: list[tuple[str, str]] = []
    heading = ""
    path: list[tuple[int, str]] = []
    buf: list[str] = []
    for line in body.splitlines():
        m = re.match(r"^(#{1,6})\s+(.*)$", line)
        if m:
            if buf:
                sections.append((heading, "\n".join(buf).strip()))
            level = len(m.group(1))
            path = [(lv, h) for lv, h in path if lv < level] + [(level, m.group(2).strip())]
            heading = " > ".join(h for lv, h in path if lv > 1) or path[-1][1]
            buf = []
        else:
            buf.append(line)
    if buf:
        sections.append((heading, "\n".join(buf).strip()))
    return [(h, t) for h, t in sections if t]


def _window(text: str) -> list[str]:
    """Char windows with overlap; keeps chunks self-contained for embedding."""
    if len(text) <= CHUNK_SIZE:
        return [text]
    out: list[str] = []
    start = 0
    while start < len(text):
        out.append(text[start : start + CHUNK_SIZE])
        start += CHUNK_SIZE - CHUNK_OVERLAP
    return out


def load_all() -> None:
    DOCS.clear(); CHUNKS.clear(); BM25_IDS.clear(); BM25_CORPUS.clear()
    for path in sorted(DOCS_DIR.rglob("*.md")):
        doc_id = path.stem
        body = path.read_text(encoding="utf-8").strip()
        title = doc_id.replace("_", " ").title()
        DOCS[doc_id] = KBDoc(doc_id=doc_id, title=title, text=body)

        n = 0

        def add(heading: str, text: str) -> None:
            nonlocal n
            chunk_id = f"{doc_id}__{n}"
            CHUNKS[chunk_id] = Chunk(chunk_id=chunk_id, doc_id=doc_id, heading=heading, text=text)
            BM25_IDS.append(chunk_id)
            BM25_CORPUS.append(_tokenize(f"{title} {heading} {text}"))
            n += 1

        # Short sections (e.g. "Email Addresses", "Location") are packed together
        # with their headings rather than dropped, so every fact stays searchable.
        pending: list[tuple[str, str]] = []

        def flush() -> None:
            if pending:
                add(" / ".join(h for h, _ in pending if h),
                    "\n\n".join(f"{h}\n{t}" if h else t for h, t in pending))
                pending.clear()

        for heading, sec_text in _split_sections(body):
            if len(sec_text) >= MIN_CHUNK_CHARS:
                flush()
                for piece in _window(sec_text):
                    add(heading, piece.strip())
                continue
            if pending and sum(len(h) + len(t) for h, t in pending) + len(sec_text) > CHUNK_SIZE:
                flush()
            pending.append((heading, sec_text))
            if sum(len(h) + len(t) for h, t in pending) >= MIN_CHUNK_CHARS:
                flush()
        flush()


load_all()
