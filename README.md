# SENTINEL — SIH 26106 Email Threat Detection & Forensics

AI-Powered Email Threat Detection, GeoLocation and Forensic Intelligence Platform.

**Operating principle:** Detect → Explain → Trace → Correlate → Preserve → Report.

## Quick start

### Prerequisites

- Python 3.11+ (local development uses the system Python)
- Node.js 20+ (for frontend)
- Docker & Docker Compose (recommended)

### Docker Compose (recommended)

```bash
./scripts/dev-start.sh
```

- Frontend: http://localhost:3000
- Backend: http://localhost:8000
- API docs: http://localhost:8000/docs

### Local development without Docker

```bash
# Setup Python venv and install dependencies
./scripts/setup.sh

# Start backend
cd backend
source ../.venv/bin/activate
uvicorn app.main:app --reload

# In another terminal, start frontend
cd frontend
npm install
npm run dev
```

### Run tests

```bash
./scripts/run-tests.sh
```

## Project structure

```text
backend/       FastAPI application
frontend/      Next.js investigation UI
docs/          Architecture, research, security, decisions
data/          Fixtures, samples, models, storage
scripts/       Development helpers
tests/         QA tests
```

## Documentation

- [Build Contract](SIH-26106-GOATED-OpenCode-Build-Contract.md)
- [Architecture v0](docs/architecture/architecture-v0.md)
- [Data Model v0](docs/architecture/data-model-v0.md)
- [API Contract v0](docs/architecture/api-contract-v0.md)
- [Threat Model v0](docs/security/threat-model-v0.md)
- [MVP Scope](docs/sih/mvp-scope.md)

## License

SIH 26106 project.
