# RAG — Retrieval-Augmented Generation Component

This directory holds the knowledge-base documents and generated vector store
for the RAG retrieval pipeline of the **Intelligent Wi-Fi Network Fault
Diagnosis and Digital Twin-Driven Recovery Recommendation System**.

---

## Directory Structure

```
rag/
├── documents/          Markdown knowledge-base files (one per fault type)
│   ├── dns_failure.md
│   ├── ethernet_problem.md
│   ├── high_latency.md
│   ├── internet_connectivity_failure.md
│   ├── network_congestion.md
│   ├── normal.md
│   ├── packet_loss.md
│   ├── router_overheating.md
│   └── weak_wifi_signal.md
│
├── vectorstore/        Generated index files (gitignored — rebuild with ingestion)
│   ├── index.faiss     FAISS IndexFlatIP — 64 vectors × 384 dims
│   └── metadata.json   Chunk text + provenance metadata (source, section, index)
│
└── README.md
```

---

## Pipeline Overview

```
documents/*.md
      │
      ▼  backend/app/rag/ingestion.py
  Load .md files  →  Markdown-section chunker  →  SentenceTransformer embeddings
                                                          │
                                                          ▼
                                              FAISS IndexFlatIP (cosine sim)
                                                          │
                                              ┌───────────┴────────────┐
                                         index.faiss            metadata.json
```

**Embedding model:** `all-MiniLM-L6-v2` (local, 384-dim, no API key needed)
**Similarity metric:** Cosine similarity via L2-normalised inner product
**Chunk strategy:** One chunk per `##` Markdown section; long sections split at
paragraph boundaries with 80-character overlap

---

## Running Ingestion

Run from the **project root** (`wifi-fault-diagnosis/`):

```bash
python scripts/test_retrieval.py
```

This script:
1. Loads all `.md` files from `rag/documents/`
2. Chunks, embeds, and indexes them into FAISS
3. Saves `index.faiss` and `metadata.json` to `rag/vectorstore/`
4. Runs 3 example retrieval queries and prints the top-3 results with scores

Ingestion is **repeatable** — re-running overwrites the existing index.

---

## Using the Retriever in Code

```python
from app.rag.retriever import retrieve_context

results = retrieve_context(
    query="What are the common causes of packet loss?",
    top_k=3,
)

for r in results:
    print(r["source"])   # e.g. "packet_loss.md"
    print(r["section"])  # e.g. "Recommended Recovery Actions"
    print(r["score"])    # cosine similarity, e.g. 0.751
    print(r["text"])     # chunk text
```

---

## Adding New Knowledge Documents

1. Create a `.md` file in `rag/documents/` using the same heading structure:
   ```markdown
   # Fault Title

   ## Description
   ## Common Symptoms
   ## Possible Causes
   ## Diagnostic Indicators
   ## Recommended Recovery Actions
   ## Verification
   ## Expected Outcome
   ```
2. Run ingestion to rebuild the index:
   ```bash
   python scripts/test_retrieval.py
   ```
3. The new document will be automatically chunked and indexed alongside the
   existing ones.

---

## Implementation Modules

| Module | Location | Purpose |
|---|---|---|
| `chunking.py` | `backend/app/rag/` | Markdown-section-aware text splitter |
| `embeddings.py` | `backend/app/rag/` | Lazy-loaded SentenceTransformer singleton |
| `ingestion.py` | `backend/app/rag/` | End-to-end ingestion pipeline |
| `retriever.py` | `backend/app/rag/` | FAISS query + top-k result formatting |
| `generator.py` | `backend/app/rag/` | LLM explanation generator *(not yet implemented)* |
| `test_retrieval.py` | `scripts/` | Standalone integration test |
