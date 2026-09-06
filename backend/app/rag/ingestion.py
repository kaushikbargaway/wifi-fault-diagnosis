"""Document ingestion for the RAG knowledge base (placeholder).

Will load documents from the rag/documents/ directory, chunk them,
generate embeddings, and store them in the vector store.
"""

from pathlib import Path


def ingest_documents(documents_dir: str = "rag/documents") -> int:
    """Ingest all documents from the given directory.

    Returns the number of documents ingested.

    TODO: Implement using LangChain / LlamaIndex document loaders.
    """
    raise NotImplementedError("Document ingestion not yet implemented.")
