#!/usr/bin/env bash
# ============================================================
# Setup script — installs Python and Node dependencies
# ============================================================
set -e

echo "==> Setting up WiFi Fault Diagnosis project ..."

# Backend
echo "\n[1/2] Installing Python dependencies ..."
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
cd ..

# Frontend
echo "\n[2/2] Installing Node dependencies ..."
cd frontend
npm install
cd ..

echo "\nSetup complete."
echo "Copy .env.example to .env and fill in your values before starting."
