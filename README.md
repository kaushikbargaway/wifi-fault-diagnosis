# Intelligent Wi-Fi Network Fault Diagnosis and Digital Twin-Driven Recovery Recommendation System

> Final Year Engineering Project

---

## Project Objective

This system monitors a Wi-Fi / network environment, collects network telemetry, diagnoses network faults using a Machine Learning (Random Forest) model, represents the network as a Digital Twin, recommends recovery actions, and generates human-readable explanations through a Retrieval-Augmented Generation (RAG) pipeline backed by a local embedding model and FAISS vector store.

**Supported environments:** homes, educational institutions, computer labs, small offices.

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        React Dashboard                          │
│  Dashboard │ Diagnosis │ Digital Twin │ Recovery │ Explanation  │
└───────────────────────────┬─────────────────────────────────────┘
                            │  HTTP / REST
┌───────────────────────────▼─────────────────────────────────────┐
│                     FastAPI Backend                             │
│  /api/v1/telemetry  │ /diagnosis │ /digital-twin │ /recovery    │
│  /api/v1/explanation│ /health                                   │
├──────────┬──────────┬──────────┬──────────────────────────────  │
│ ML Layer │ Dig-Twin │ RAG      │  Database (SQLite → Postgres)  │
│ (RF)     │ (2× VM)  │ (FAISS)  │                                │
└──────────┴──────────┴──────────┴────────────────────────────────┘
            ▲                ▲
            │                │ Knowledge Base (rag/documents/)
            │  Telemetry     │ Vector Store   (rag/vectorstore/)
┌───────────┴──────────────────────┐
│  ESP32 / Simulated Telemetry     │
└──────────────────────────────────┘
```

---

## Technology Stack

| Layer | Technology |
|-------|------------|
| Backend | Python 3.11, FastAPI, Uvicorn, Pydantic v2 |
| ML | scikit-learn (Random Forest), NumPy, Pandas |
| Database | SQLAlchemy, SQLite (dev) / PostgreSQL (prod) |
| RAG | FAISS (`faiss-cpu`), Sentence-Transformers (`all-MiniLM-L6-v2`) |
| LLM *(planned)* | LangChain / OpenAI / Ollama (configurable) |
| Frontend | React 18, Vite, React Router, Recharts |
| Digital Twin | Ubuntu VMs, tc/netem, SSH |
| IoT Layer | ESP32 (or simulated telemetry) |
| Containers | Docker, Docker Compose |

---

## Repository Structure

```
wifi-fault-diagnosis/
├── backend/                  FastAPI backend
│   ├── app/
│   │   ├── api/              REST route handlers
│   │   ├── core/
│   │   │   ├── config.py     Centralised settings (env-var driven)
│   │   │   └── paths.py      Centralised path resolution helper
│   │   ├── ml/               Random Forest diagnosis service
│   │   ├── digital_twin/     Digital Twin SSH controller
│   │   └── rag/              RAG retrieval pipeline
│   │       ├── chunking.py   Markdown-section-aware text splitter
│   │       ├── embeddings.py Local SentenceTransformer singleton
│   │       ├── ingestion.py  Load → chunk → embed → FAISS → save
│   │       ├── retriever.py  FAISS query → top-k results + metadata
│   │       └── generator.py  LLM explanation generator (planned)
│   └── requirements.txt
│
├── frontend/                 React + Vite dashboard
├── ml/                       Standalone ML notebooks, scripts, datasets
├── digital-twin/             VM configs, scenarios, automation scripts
├── esp32/                    Firmware and sensor code for ESP32
│
├── rag/
│   ├── documents/            Markdown knowledge-base (one file per fault)
│   ├── vectorstore/          Generated FAISS index (gitignored)
│   └── README.md
│
├── docs/                     Architecture, API, deployment documentation
├── scripts/
│   ├── test_retrieval.py     RAG pipeline integration test
│   └── setup.sh / start_*.sh
└── .env.example
```

See each subdirectory's `README.md` for component-specific details.

---

## Setup Instructions

### Prerequisites

- Python 3.11+
- Node.js 20+
- npm 10+
- Docker + Docker Compose (optional but recommended)

### 1. Clone and enter the repository

```bash
git clone <repo-url>
cd wifi-fault-diagnosis
```

### 2. Copy the environment file

```bash
cp .env.example .env
# Edit .env with your actual values
```

### 3. Backend

```bash
cd backend
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux / macOS:
source .venv/bin/activate

pip install -r requirements.txt
```

### 4. Build the RAG vector store

Run once from the **project root** after installing backend dependencies:

```bash
python scripts/test_retrieval.py
```

This loads the 9 knowledge-base documents from `rag/documents/`, chunks them,
generates embeddings with `all-MiniLM-L6-v2`, and saves the FAISS index to
`rag/vectorstore/`. Re-run any time you add or update knowledge-base files.

### 5. Frontend

```bash
cd frontend
npm install
```

---

## Development Workflow

### Start the backend

```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

API docs available at: <http://localhost:8000/docs>

### Start the frontend

```bash
cd frontend
npm run dev
```

Dashboard available at: <http://localhost:5173>

### Start both with Docker Compose

```bash
docker-compose up --build
```

---

## Environment Variables

See [`.env.example`](.env.example) for the full list.

Key variables:

| Variable | Purpose | Default |
|----------|---------|---------| 
| `DATABASE_URL` | Database connection string | `sqlite:///./wifi_fault.db` |
| `USE_SIMULATED_TELEMETRY` | Use simulated data instead of ESP32 | `true` |
| `EMBEDDING_MODEL` | Sentence-Transformers model for RAG | `all-MiniLM-L6-v2` |
| `DOCUMENTS_PATH` | Path to knowledge-base documents | `rag/documents` |
| `VECTORSTORE_PATH` | Path to FAISS vector store | `rag/vectorstore` |
| `LLM_PROVIDER` | LLM backend (`openai` / `ollama`) | `openai` |
| `LLM_API_KEY` | API key for the LLM provider | *(empty)* |
| `DT_VM1_HOST` / `DT_VM2_HOST` | Digital Twin VM addresses | `192.168.56.101/102` |

---

## Testing

```bash
# Backend unit tests
cd backend
pytest tests/ -v

# RAG pipeline integration test (runs from project root)
python scripts/test_retrieval.py

# Frontend tests
cd frontend
npm test
```

---

## Fault Categories

| Label | Description |
|-------|-------------|
| `normal` | Network operating normally |
| `weak_wifi_signal` | RSSI below acceptable threshold |
| `high_latency` | Round-trip latency excessively high |
| `packet_loss` | Significant packet loss detected |
| `dns_failure` | DNS resolution failing |
| `internet_connectivity_failure` | No WAN reachability |
| `ethernet_problem` | Ethernet link down |
| `router_overheating` | Device temperature above threshold |
| `network_congestion` | Network load causing degradation |

---

## RAG Pipeline Status

The retrieval pipeline is **fully implemented and tested**:

| Module | Status |
|--------|--------|
| `chunking.py` — Markdown-section chunker | ✅ Complete |
| `embeddings.py` — `all-MiniLM-L6-v2` singleton | ✅ Complete |
| `ingestion.py` — FAISS index builder | ✅ Complete |
| `retriever.py` — top-k semantic search | ✅ Complete |
| `core/paths.py` — centralised path resolution | ✅ Complete |
| `generator.py` — LLM explanation generator | 🔲 Planned |

Vector store: **64 chunks** indexed from 9 fault-type knowledge-base documents.
Embedding dimension: **384** · Similarity metric: **cosine** (via `IndexFlatIP` + L2 normalisation).

---

## Project Status

| Component | Status |
|-----------|--------|
| Project structure & configuration | ✅ Complete |
| Random Forest diagnosis model | ✅ Complete |
| RAG retrieval pipeline | ✅ Complete |
| FastAPI backend (routes & services) | 🔧 In Progress |
| Digital Twin (VM simulation) | 🔧 In Progress |
| React dashboard (frontend) | 🔧 In Progress |
| LLM explanation generator | 🔲 Planned |
| ESP32 firmware | 🔲 Planned |
