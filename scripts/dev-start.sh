#!/usr/bin/env bash
set -e

echo "[SENTINEL] Starting development services with Docker Compose..."

docker compose up --build -d

echo "[SENTINEL] Services starting..."
echo "  Frontend: http://localhost:3000"
echo "  Backend:  http://localhost:8000"
echo "  API docs: http://localhost:8000/docs"
echo ""
echo "Run 'docker compose logs -f backend' to view backend logs."
