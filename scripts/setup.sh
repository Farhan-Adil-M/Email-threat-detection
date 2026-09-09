#!/usr/bin/env bash
set -e

echo "[SENTINEL] Setting up local development environment..."

# Backend
if [ ! -d "backend/.venv" ]; then
    echo "[SENTINEL] Creating Python virtual environment..."
    python3 -m venv backend/.venv
fi

echo "[SENTINEL] Installing backend dependencies..."
backend/.venv/bin/pip install --upgrade pip
backend/.venv/bin/pip install -r backend/requirements.txt

# Frontend
echo "[SENTINEL] Installing frontend dependencies..."
cd frontend
npm install
cd ..

# Environment file
if [ ! -f ".env" ]; then
    echo "[SENTINEL] Creating .env from example..."
    cp .env.example .env
fi

# Storage directory
mkdir -p backend/data/storage

echo "[SENTINEL] Setup complete. Run ./scripts/dev-start.sh to start services."
