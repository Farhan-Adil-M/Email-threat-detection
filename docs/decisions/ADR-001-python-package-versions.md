# ADR-001 — Python Package Version Strategy

## Status

Accepted

## Context

The local development environment runs Python 3.14. Many pinned package versions (e.g., pydantic-core 2.7, psycopg2-binary 2.9) do not yet provide prebuilt wheels for Python 3.14, causing source builds to fail or time out.

## Decision

Use flexible version ranges (`>=,<`) for core dependencies in `backend/requirements.txt` during active development, allowing pip to resolve versions compatible with the local interpreter. The production Docker image uses `python:3.11-slim`, where stable pinned versions are preferred.

## Tradeoffs

- **Pros:** Local development works on Python 3.14 without waiting for every dependency wheel.
- **Cons:** Reproducibility is weaker than with exact pins. We will re-pin to a `requirements-lock.txt` before final demo.

## Consequences

- CI/CD and Docker builds must validate against a lockfile in the future.
- ML/analysis libraries (scikit-learn, numpy, dnspython, etc.) are deferred to their respective implementation phases to avoid long source builds during Foundation.

## Date

2026-09-09
