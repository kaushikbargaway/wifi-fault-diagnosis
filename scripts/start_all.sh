#!/usr/bin/env bash
# Start both backend and frontend in parallel
set -e
trap 'kill 0' EXIT

bash scripts/start_backend.sh &
bash scripts/start_frontend.sh &

wait
