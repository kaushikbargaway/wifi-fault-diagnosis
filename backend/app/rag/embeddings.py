"""Embedding generation using a local Sentence-Transformers model.

The model is loaded **once** on first use (lazy singleton) and reused for all
subsequent calls.  No network requests are made after the initial model
download — inference runs entirely on the local CPU.

Configuration
-------------
The embedding model name is read from ``settings.EMBEDDING_MODEL``.
The default (``all-MiniLM-L6-v2``) produces 384-dimensional vectors and
offers a good balance of speed and quality for semantic search.
"""

from __future__ import annotations

import logging
from typing import List, Optional

import numpy as np

from app.core.config import settings

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Lazy singleton — model is loaded on first call, then reused.
# ---------------------------------------------------------------------------

_model = None  # type: Optional[object]  # SentenceTransformer instance


def _get_model():
    """Return the shared SentenceTransformer instance, loading it on first use."""
    global _model
    if _model is None:
        try:
            from sentence_transformers import SentenceTransformer  # type: ignore
        except ImportError as exc:
            raise ImportError(
                "sentence-transformers is not installed.  "
                "Run: pip install sentence-transformers>=3.0.0"
            ) from exc

        model_name: str = settings.EMBEDDING_MODEL
        logger.info("Loading embedding model '%s' …", model_name)
        _model = SentenceTransformer(model_name)
        logger.info("Embedding model loaded (dim=%d).", _model.get_embedding_dimension())

    return _model


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def embed_texts(texts: List[str]) -> np.ndarray:
    """Generate L2-normalised embeddings for a list of text strings.

    Parameters
    ----------
    texts:
        Non-empty list of strings to embed.

    Returns
    -------
    np.ndarray
        Float32 array of shape ``(len(texts), embedding_dim)``.
        Vectors are L2-normalised so that inner-product search equals
        cosine similarity.

    Raises
    ------
    ValueError
        If *texts* is empty.
    """
    if not texts:
        raise ValueError("embed_texts received an empty list of texts.")

    model = _get_model()
    logger.debug("Embedding %d text(s) …", len(texts))
    vectors = model.encode(
        texts,
        batch_size=32,
        show_progress_bar=False,
        normalize_embeddings=True,   # L2-norm → inner product == cosine sim
        convert_to_numpy=True,
    )
    return vectors.astype(np.float32)


def embed_query(query: str) -> np.ndarray:
    """Embed a single query string.

    Parameters
    ----------
    query:
        The search query.  Must be a non-empty string.

    Returns
    -------
    np.ndarray
        Float32 array of shape ``(1, embedding_dim)``, L2-normalised.

    Raises
    ------
    ValueError
        If *query* is empty or whitespace-only.
    """
    query = query.strip()
    if not query:
        raise ValueError("Query must be a non-empty string.")

    return embed_texts([query])


def get_embedding_dim() -> int:
    """Return the dimensionality of the loaded embedding model."""
    return _get_model().get_embedding_dimension()
