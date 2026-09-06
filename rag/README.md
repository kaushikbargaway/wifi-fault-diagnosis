# RAG — Retrieval-Augmented Generation Component

This directory holds the knowledge documents and (gitignored) vector store for the RAG pipeline.

## Structure

```
rag/
├── documents/     Source documents ingested into the knowledge base
├── vectorstore/   Generated vector embeddings (gitignored)
└── README.md
```

## Adding Knowledge Documents

1. Place `.txt`, `.md`, or `.pdf` files in `rag/documents/`.
2. Run the ingestion script (to be implemented in `backend/app/rag/ingestion.py`).
3. The pipeline will chunk, embed, and store the documents in the vector store.

## Suggested Documents

- Wi-Fi troubleshooting guides.
- IEEE 802.11 standard summaries.
- Router manufacturer manuals.
- Network fault diagnosis references.
