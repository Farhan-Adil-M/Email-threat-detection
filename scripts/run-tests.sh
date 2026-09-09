#!/usr/bin/env bash
set -e

echo "[SENTINEL] Running test suite..."

# Backend tests
cd backend
../.venv/bin/pytest tests/ -v
cd ..

# Frontend typecheck
cd frontend
npm run typecheck
cd ..

echo "[SENTINEL] Tests complete."
