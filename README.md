# Intelligent Wi-Fi Network Fault Diagnosis and Digital Twin-Driven Recovery Recommendation System

> Final Year Engineering Project

---

## Project Objective

This system monitors a Wi-Fi / network environment, collects network telemetry, diagnoses network faults using a Machine Learning (Random Forest) model, represents the network as a Digital Twin, recommends recovery actions, and generates human-readable explanations through a Retrieval-Augmented Generation (RAG) / LLM pipeline.

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
│ ML Layer │ Dig-Twin │ RAG/LLM  │  Database (SQLite → Postgres)  │
│ (RF)     │ (2× VM)  │          │                                │
└──────────┴──────────┴──────────┴────────────────────────────────┘
            ▲
            │  Telemetry (RSSI, latency, packet loss …)
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
| RAG / LLM | LangChain / OpenAI / Ollama (configurable) |
| Frontend | React 18, Vite, React Router, Recharts |
| Digital Twin | Ubuntu VMs, tc/netem, SSH |
| IoT Layer | ESP32 (or simulated telemetry) |
| Containers | Docker, Docker Compose |

---

## Repository Structure

```
wifi-fault-diagnosis/
├── backend/          FastAPI backend (ML, RAG, Digital Twin services)
├── frontend/         React + Vite dashboard
├── ml/               Standalone ML notebooks, scripts, datasets, models
├── digital-twin/     VM configs, scenarios, automation scripts
├── esp32/            Firmware and sensor code for ESP32
├── rag/              Knowledge documents and vector store
├── docs/             Architecture, API, deployment documentation
└── scripts/          Setup and startup shell scripts
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

### 4. Frontend

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
| `LLM_PROVIDER` | LLM backend (`openai` / `ollama`) | `openai` |
| `LLM_API_KEY` | API key for the LLM provider | *(empty)* |
| `DT_VM1_HOST` / `DT_VM2_HOST` | Digital Twin VM addresses | `192.168.56.101/102` |

---

## Testing

```bash
# Backend tests
cd backend
pytest tests/ -v

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

## Project Status

Currently in **Phase 1 — Project Structure**. All feature modules are placeholders and will be implemented in subsequent phases.
