"""Embedding generation (placeholder).

Supports multiple embedding backends configurable via settings.
"""

from typing import List
from app.core.config import settings


def embed_texts(texts: List[str]) -> List[List[float]]:
    """Generate embeddings for a list of text chunks.

    TODO: Implement using the configured embedding model
    (e.g. OpenAI text-embedding-ada-002, or a local HuggingFace model).
    """
    raise NotImplementedError("Embedding generation not yet implemented.")
