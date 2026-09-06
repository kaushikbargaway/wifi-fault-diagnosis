#!/usr/bin/env bash
# Start the FastAPI backend with Uvicorn hot-reload
set -e
cd backend
source .venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
