"""FAISS-backed retriever for the RAG pipeline.

The retriever loads the FAISS index and metadata JSON **lazily** on the first
call to ``retrieve_context()``.  Subsequent calls reuse the in-memory cache,
so there is no per-request disk I/O.

Return format
-------------
``retrieve_context()`` returns a list of dicts:

.. code-block:: python

    [
        {
            "text": "...",           # chunk text
            "source": "packet_loss.md",
            "section": "Recommended Recovery Actions",
            "chunk_index": 4,
            "score": 0.87,          # cosine similarity (0–1)
        },
        ...
    ]

Integration with generator.py
------------------------------
Pass the returned list directly to ``generate_explanation()``; the generator
can access ``item["text"]`` for context and ``item["source"]`` / ``item["section"]``
for citations.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import List, Optional

from app.core.paths import get_vectorstore_dir, resolve_path

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Module-level cache (lazy-loaded on first retrieve call)
# ---------------------------------------------------------------------------

_index = None   # faiss.Index instance
_metadata: Optional[List[dict]] = None   # parallel list of chunk metadata


def _load_index(vectorstore_dir: Path) -> None:
    """Populate the module-level cache from disk."""
    global _index, _metadata

    index_file = vectorstore_dir / "index.faiss"
    meta_file = vectorstore_dir / "metadata.json"

    if not index_file.exists():
        raise FileNotFoundError(
            f"FAISS index not found at '{index_file}'.\n"
            "Run ingestion first:  python scripts/test_retrieval.py  "
            "or  python -m backend.app.rag.ingestion"
        )
    if not meta_file.exists():
        raise FileNotFoundError(
            f"Metadata file not found at '{meta_file}'.\n"
            "Re-run ingestion to regenerate both files."
        )

    try:
        import faiss  # type: ignore
    except ImportError as exc:
        raise ImportError(
            "faiss-cpu is not installed.  Run: pip install faiss-cpu>=1.8.0"
        ) from exc

    _index = faiss.read_index(str(index_file))
    _metadata = json.loads(meta_file.read_text(encoding="utf-8"))
    logger.info(
        "Loaded FAISS index (%d vectors) and metadata (%d entries).",
        _index.ntotal,
        len(_metadata),
    )


def _ensure_loaded(vectorstore_dir: Path | None = None) -> None:
    """Load the index from disk if it has not been loaded yet."""
    global _index, _metadata
    if _index is None or _metadata is None:
        vs_path = vectorstore_dir or get_vectorstore_dir()
        _load_index(vs_path)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def retrieve_context(
    query: str,
    top_k: int = 3,
    vectorstore_dir: str | None = None,
) -> List[dict]:
    """Retrieve the most relevant knowledge-base chunks for *query*.

    Parameters
    ----------
    query:
        The natural-language query string.
    top_k:
        Number of results to return (default: 3).
    vectorstore_dir:
        Optional override for the vector store directory path.
        Resolved relative to the project root if given as a relative string.

    Returns
    -------
    List[dict]
        Ordered list (highest similarity first) of dicts with keys:
        ``text``, ``source``, ``section``, ``chunk_index``, ``score``.

    Raises
    ------
    ValueError
        If *query* is empty or whitespace-only.
    FileNotFoundError
        If the FAISS index or metadata file cannot be found.
    """
    # -- validate query -------------------------------------------------------
    query = query.strip()
    if not query:
        raise ValueError("Query must be a non-empty string.")

    if top_k < 1:
        raise ValueError(f"top_k must be >= 1, got {top_k}.")

    # -- lazy-load index ------------------------------------------------------
    vs_override = resolve_path(vectorstore_dir) if vectorstore_dir else None
    _ensure_loaded(vs_override)

    assert _index is not None and _metadata is not None  # for type checkers

    # -- embed query ----------------------------------------------------------
    from app.rag.embeddings import embed_query

    query_vec = embed_query(query)  # shape: (1, D), float32, L2-normalised

    # -- search ---------------------------------------------------------------
    effective_k = min(top_k, _index.ntotal)
    scores, indices = _index.search(query_vec, effective_k)  # (1, k)

    # -- assemble results -----------------------------------------------------
    results: List[dict] = []
    for score, idx in zip(scores[0], indices[0]):
        if idx == -1:
            # FAISS returns -1 for padded results when ntotal < k
            continue
        entry = _metadata[idx]
        results.append(
            {
                "text": entry["text"],
                "source": entry.get("source", "unknown"),
                "section": entry.get("section", ""),
                "chunk_index": entry.get("chunk_index", idx),
                "score": float(score),
            }
        )

    logger.debug(
        "Query: %r → %d result(s) (top score=%.4f).",
        query[:60],
        len(results),
        results[0]["score"] if results else 0.0,
    )
    return results


def reload_index() -> None:
    """Force a reload of the FAISS index from disk.

    Useful after re-running ingestion while the application is running.
    """
    global _index, _metadata
    _index = None
    _metadata = None
    _ensure_loaded()
    logger.info("Index reloaded successfully.")
