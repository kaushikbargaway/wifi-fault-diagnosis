"""Centralised path resolution for the WiFi Fault Diagnosis project.

All RAG modules (ingestion, retriever, embeddings) and utility scripts should
import from here instead of computing paths locally.

Design
------
* ``get_project_root()`` discovers the project root **by sentinel** (looks for a
  directory containing both ``rag/`` and ``backend/`` subdirectories), so it
  works regardless of where Python is invoked from or where this file sits in
  the tree.  Result is cached with ``functools.lru_cache``.

* ``resolve_path(path)`` handles both absolute and relative inputs safely:
  - Absolute paths are returned as-is (no accidental re-rooting).
  - Relative paths are resolved relative to the project root.

* Convenience accessors ``get_documents_dir()`` and ``get_vectorstore_dir()``
  read ``settings.DOCUMENTS_PATH`` / ``settings.VECTORSTORE_PATH`` and
  resolve them through ``resolve_path()``, so a value like
  ``VECTORSTORE_PATH=/data/vectorstore`` (absolute) works just as well as the
  default relative value ``rag/vectorstore``.

Usage
-----
    from app.core.paths import resolve_path, get_documents_dir, get_vectorstore_dir

    docs  = get_documents_dir()      # → Path(".../wifi-fault-diagnosis/rag/documents")
    store = get_vectorstore_dir()    # → Path(".../wifi-fault-diagnosis/rag/vectorstore")

    # Or resolve an arbitrary config value:
    model = resolve_path(settings.MODEL_PATH)
"""

from __future__ import annotations

import logging
from functools import lru_cache
from pathlib import Path

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Project-root discovery
# ---------------------------------------------------------------------------

_SENTINEL_DIRS = frozenset({"rag", "backend"})  # both must exist at root level


@lru_cache(maxsize=1)
def get_project_root() -> Path:
    """Return the absolute path to the project root (``wifi-fault-diagnosis/``).

    Discovery strategy
    ------------------
    Walk upward from this file's directory until we find a directory that
    contains **both** ``rag/`` and ``backend/`` subdirectories.  This is
    robust to the file being moved within the tree and does not hard-code a
    fixed number of ``parent`` hops.

    If no sentinel directory is found within 8 levels (which should never
    happen in this project), a ``RuntimeError`` is raised with a helpful
    message rather than silently returning a wrong path.

    Returns
    -------
    Path
        Absolute, resolved project root directory.
    """
    candidate = Path(__file__).resolve().parent

    for _ in range(8):
        if _SENTINEL_DIRS.issubset({p.name for p in candidate.iterdir() if p.is_dir()}):
            logger.debug("Project root resolved to: %s", candidate)
            return candidate
        candidate = candidate.parent

    raise RuntimeError(
        "Could not locate the project root.  "
        f"Expected a directory containing both {sorted(_SENTINEL_DIRS)} subdirectories "
        f"within 8 levels of '{Path(__file__).resolve()}'.  "
        "Make sure the project structure has not been altered."
    )


# ---------------------------------------------------------------------------
# Path resolution
# ---------------------------------------------------------------------------

def resolve_path(path: str | Path) -> Path:
    """Resolve *path* to an absolute ``Path``.

    Parameters
    ----------
    path:
        A filesystem path as a string or ``pathlib.Path``.

        * **Absolute** paths are returned unchanged (no re-rooting).
        * **Relative** paths are resolved relative to the project root
          returned by ``get_project_root()``.

    Returns
    -------
    Path
        An absolute, resolved ``Path`` object.

    Examples
    --------
    >>> resolve_path("rag/vectorstore")
    PosixPath('/home/user/wifi-fault-diagnosis/rag/vectorstore')

    >>> resolve_path("/data/custom_vectorstore")
    PosixPath('/data/custom_vectorstore')
    """
    p = Path(path)
    if p.is_absolute():
        return p.resolve()
    return (get_project_root() / p).resolve()


# ---------------------------------------------------------------------------
# Convenience accessors (read settings lazily to avoid circular imports)
# ---------------------------------------------------------------------------

def get_documents_dir() -> Path:
    """Return the resolved absolute path to the knowledge-base documents directory.

    Reads ``settings.DOCUMENTS_PATH`` and passes it through ``resolve_path()``,
    so both relative (``rag/documents``) and absolute paths work correctly.
    """
    from app.core.config import settings  # late import avoids circular dependency
    return resolve_path(settings.DOCUMENTS_PATH)


def get_vectorstore_dir() -> Path:
    """Return the resolved absolute path to the FAISS vector-store directory.

    Reads ``settings.VECTORSTORE_PATH`` and passes it through ``resolve_path()``,
    so both relative (``rag/vectorstore``) and absolute paths work correctly.
    """
    from app.core.config import settings  # late import avoids circular dependency
    return resolve_path(settings.VECTORSTORE_PATH)
