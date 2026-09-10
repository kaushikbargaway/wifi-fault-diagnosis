"""Document ingestion pipeline for the RAG knowledge base.

Pipeline
--------
1. Load all ``.md`` files from the configured documents directory.
2. Chunk each document using the Markdown-aware chunker.
3. Generate L2-normalised embeddings with the local Sentence-Transformers model.
4. Build a FAISS ``IndexFlatIP`` index (inner product on normalised vectors
   equals cosine similarity).
5. Persist the FAISS index and the corresponding metadata list to
   ``rag/vectorstore/``.

Ingestion is **repeatable** — running it again overwrites the existing index.

Usage (from the project root)
------------------------------
    python -m backend.app.rag.ingestion
    # or
    from backend.app.rag.ingestion import ingest_documents
    count = ingest_documents()
"""

from __future__ import annotations

import json
import logging
import sys
from pathlib import Path
from typing import List

from app.core.paths import get_documents_dir, get_vectorstore_dir, resolve_path

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Document loader
# ---------------------------------------------------------------------------

def _load_documents(documents_dir: Path) -> List[dict]:
    """Load all ``.md`` files from *documents_dir*.

    Returns
    -------
    List[dict]
        Each entry is ``{"text": str, "source": str (absolute path)}``.

    Raises
    ------
    FileNotFoundError
        If *documents_dir* does not exist.
    ValueError
        If no ``.md`` files are found.
    """
    if not documents_dir.exists():
        raise FileNotFoundError(
            f"Documents directory not found: {documents_dir}\n"
            "Create the directory and add .md knowledge-base files."
        )

    md_files = sorted(documents_dir.glob("*.md"))
    if not md_files:
        raise ValueError(
            f"No .md files found in '{documents_dir}'. "
            "Add Markdown knowledge-base files and run ingestion again."
        )

    documents: List[dict] = []
    for path in md_files:
        text = path.read_text(encoding="utf-8").strip()
        if text:
            documents.append({"text": text, "source": str(path)})
            logger.debug("Loaded document: %s (%d chars)", path.name, len(text))
        else:
            logger.warning("Skipping empty file: %s", path.name)

    logger.info("Loaded %d document(s) from '%s'.", len(documents), documents_dir)
    return documents


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def ingest_documents(
    documents_dir: str | None = None,
    vectorstore_dir: str | None = None,
) -> int:
    """Run the full ingestion pipeline and persist the FAISS index.

    Parameters
    ----------
    documents_dir:
        Path to the directory containing ``.md`` knowledge-base files.
        Defaults to ``settings.DOCUMENTS_PATH`` resolved from the project root.
    vectorstore_dir:
        Path to the directory where ``index.faiss`` and ``metadata.json``
        will be saved.  Defaults to ``settings.VECTORSTORE_PATH`` resolved
        from the project root.

    Returns
    -------
    int
        Total number of chunks indexed.

    Raises
    ------
    FileNotFoundError
        If the documents directory does not exist.
    ValueError
        If no documents or no text is found.
    ImportError
        If ``faiss`` or ``sentence-transformers`` are not installed.
    """
    try:
        import faiss  # type: ignore
    except ImportError as exc:
        raise ImportError(
            "faiss-cpu is not installed.  Run: pip install faiss-cpu>=1.8.0"
        ) from exc

    # -- resolve paths -------------------------------------------------------
    # resolve_path() handles both absolute overrides and relative defaults:
    # relative paths are anchored to the project root, absolute paths are kept.
    docs_path = resolve_path(documents_dir) if documents_dir else get_documents_dir()
    vs_path = resolve_path(vectorstore_dir) if vectorstore_dir else get_vectorstore_dir()

    logger.info("Documents : %s", docs_path)
    logger.info("Vectorstore: %s", vs_path)

    # -- load documents -------------------------------------------------------
    documents = _load_documents(docs_path)

    # -- chunk ----------------------------------------------------------------
    from app.rag.chunking import chunk_documents

    chunks = chunk_documents(documents)
    logger.info("Created %d chunk(s) from %d document(s).", len(chunks), len(documents))

    # -- embed ----------------------------------------------------------------
    from app.rag.embeddings import embed_texts, get_embedding_dim

    texts = [c.text for c in chunks]
    vectors = embed_texts(texts)          # shape: (N, D), float32, L2-normalised
    dim = get_embedding_dim()

    # -- build FAISS index (IndexFlatIP + normalised vecs = cosine sim) -------
    index = faiss.IndexFlatIP(dim)
    index.add(vectors)
    logger.info("FAISS index built: %d vector(s), dim=%d.", index.ntotal, dim)

    # -- persist --------------------------------------------------------------
    vs_path.mkdir(parents=True, exist_ok=True)

    index_file = vs_path / "index.faiss"
    meta_file = vs_path / "metadata.json"

    faiss.write_index(index, str(index_file))
    logger.info("Saved FAISS index → %s", index_file)

    metadata = [c.metadata | {"text": c.text} for c in chunks]
    meta_file.write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    logger.info("Saved metadata   → %s", meta_file)

    return len(chunks)


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import os

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )

    # Allow running from the project root or from backend/
    from app.core.paths import get_project_root
    root = get_project_root()
    sys.path.insert(0, str(root / "backend"))
    os.chdir(root)

    total = ingest_documents()
    print(f"\nIngestion complete — {total} chunks indexed.")
