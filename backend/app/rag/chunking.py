"""Markdown-aware text chunking for the RAG pipeline.

Strategy
--------
Each ``##`` heading in a knowledge-base document defines a logical section
that we want to keep intact.  The chunker:

1. Splits the raw Markdown on ``##`` headings to extract named sections.
2. Keeps each section as a single chunk when it fits within *max_chars*.
3. Splits oversized sections at paragraph boundaries (blank lines), applying
   a character-level overlap so context is not lost at split points.
4. Attaches metadata (source filename, section heading, chunk index) to every
   chunk so the retriever can surface provenance information.

No external dependencies — pure Python only.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import List


# ---------------------------------------------------------------------------
# Public types
# ---------------------------------------------------------------------------

class Chunk:
    """A single text chunk with attached metadata."""

    __slots__ = ("text", "metadata")

    def __init__(self, text: str, metadata: dict) -> None:
        self.text = text
        self.metadata = metadata  # source, section, chunk_index, char_start

    def __repr__(self) -> str:  # pragma: no cover
        src = self.metadata.get("source", "?")
        sec = self.metadata.get("section", "?")
        return f"<Chunk source={src!r} section={sec!r} len={len(self.text)}>"


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _split_on_paragraphs(text: str, max_chars: int, overlap: int) -> List[str]:
    """Split *text* at blank-line boundaries with character-level overlap.

    Paragraphs that are individually longer than *max_chars* are included as
    single chunks rather than broken mid-word (they are rare in our KB docs).
    """
    paragraphs = re.split(r"\n{2,}", text.strip())
    chunks: List[str] = []
    current = ""

    for para in paragraphs:
        para = para.strip()
        if not para:
            continue
        candidate = (current + "\n\n" + para).strip() if current else para
        if len(candidate) <= max_chars:
            current = candidate
        else:
            if current:
                chunks.append(current)
                # Carry the tail of *current* into the next chunk for overlap.
                overlap_text = current[-overlap:] if len(current) > overlap else current
                current = (overlap_text + "\n\n" + para).strip()
            else:
                # Single paragraph already exceeds max_chars — keep it whole.
                current = para

    if current:
        chunks.append(current)

    return chunks or [text.strip()]


def _parse_sections(raw: str) -> List[tuple[str, str]]:
    """Return a list of (heading, body) pairs parsed from Markdown text.

    The document title (``# …``) is treated as a preamble attached to the
    first real section so it is never silently discarded.
    """
    # Split on level-2 headings (##), keeping the heading text.
    parts = re.split(r"^(##\s+.+)$", raw, flags=re.MULTILINE)

    sections: List[tuple[str, str]] = []
    preamble = parts[0].strip()  # text before the first ## heading

    i = 1
    while i < len(parts) - 1:
        heading = parts[i].strip().lstrip("#").strip()
        body = parts[i + 1].strip()
        if preamble:
            # Prepend the preamble (document title + description) to the
            # first section so those lines are not orphaned.
            body = preamble + "\n\n" + body
            preamble = ""
        sections.append((heading, body))
        i += 2

    # If the document has no ## headings, treat the whole text as one section.
    if not sections:
        sections.append(("Document", raw.strip()))

    return sections


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def chunk_documents(
    documents: List[dict],
    max_chars: int = 600,
    overlap: int = 80,
) -> List[Chunk]:
    """Chunk a list of loaded documents into retrieval-ready ``Chunk`` objects.

    Parameters
    ----------
    documents:
        List of ``{"text": str, "source": str}`` dicts as returned by the
        document loader in ``ingestion.py``.
    max_chars:
        Maximum character length for a single chunk.  Sections shorter than
        this are kept intact; longer ones are split at paragraph boundaries.
    overlap:
        Number of characters from the end of the previous sub-chunk to
        prepend to the next, preserving cross-boundary context.

    Returns
    -------
    List[Chunk]
        Ordered list of chunks ready for embedding.

    Raises
    ------
    ValueError
        If *documents* is empty or any document has no text.
    """
    if not documents:
        raise ValueError("chunk_documents received an empty document list.")

    all_chunks: List[Chunk] = []
    chunk_index = 0

    for doc in documents:
        text: str = doc.get("text", "").strip()
        source: str = doc.get("source", "unknown")

        if not text:
            raise ValueError(f"Document '{source}' contains no text.")

        sections = _parse_sections(text)

        for heading, body in sections:
            if len(body) <= max_chars:
                # Section fits in one chunk — keep it whole.
                sub_chunks = [body]
            else:
                sub_chunks = _split_on_paragraphs(body, max_chars, overlap)

            for sub in sub_chunks:
                sub = sub.strip()
                if not sub:
                    continue
                all_chunks.append(
                    Chunk(
                        text=sub,
                        metadata={
                            "source": Path(source).name,
                            "section": heading,
                            "chunk_index": chunk_index,
                        },
                    )
                )
                chunk_index += 1

    return all_chunks
