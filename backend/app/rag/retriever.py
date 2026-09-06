"""Vector store retrieval (placeholder)."""

from typing import List
from app.core.config import settings


def retrieve_context(query: str, top_k: int = 3) -> List[str]:
    """Retrieve the most relevant document chunks for the given query.

    Returns a list of text chunks. Returns empty list when the vector
    store is not yet populated.

    TODO: Implement using FAISS, Chroma, or another vector database.
    """
    # Placeholder — return an empty context until the RAG pipeline is built.
    return []
