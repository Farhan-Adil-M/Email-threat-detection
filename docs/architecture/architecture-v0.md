# Architecture v0 — SIH 26106 SENTINEL

## Overview

SENTINEL is a modular-monolith email forensic investigation platform.

Operating principle: **Detect → Explain → Trace → Correlate → Preserve → Report.**

## High-level architecture

```text
                          ┌─────────────────────┐
                          │       ANALYST       │
                          └──────────┬──────────┘
                                     │
                                     ▼
                          ┌─────────────────────┐
                          │     NEXT.JS WEB     │
                          │ Investigation UI    │
                          └──────────┬──────────┘
                                     │ REST
                                     ▼
                          ┌─────────────────────┐
                          │       FASTAPI       │
                          │ API / auth / cases  │
                          └──────────┬──────────┘
                                     │
                                     ▼
                          ┌─────────────────────┐
                          │   REDIS JOB QUEUE   │
                          └──────────┬──────────┘
                                     │
                ┌────────────────────┼────────────────────┐
                ▼                    ▼                    ▼
         ┌──────────────┐    ┌──────────────┐    ┌──────────────┐
         │  FORENSICS   │    │  INTELLIGENCE│    │      ML      │
         │              │    │              │    │              │
         │ parser       │    │ DNS          │    │ features     │
         │ headers      │    │ RDAP         │    │ classifier   │
         │ Received     │    │ IP           │    │ probabilities│
         │ SPF/DKIM     │    │ reputation   │    │              │
         │ DMARC        │    │ URLs         │    │              │
         └──────┬───────┘    └──────┬───────┘    └──────┬───────┘
                └────────────────────┼────────────────────┘
                                     ▼
                          ┌─────────────────────┐
                          │  EVIDENCE FUSION    │
                          └──────────┬──────────┘
                                     ▼
                          ┌─────────────────────┐
                          │     RISK ENGINE     │
                          └──────────┬──────────┘
                                     │
                      ┌──────────────┴──────────────┐
                      ▼                             ▼
               ┌──────────────┐             ┌──────────────┐
               │ GRAPH ENGINE │             │ CAMPAIGN     │
               │              │             │ CORRELATION  │
               └──────┬───────┘             └──────┬───────┘
                      └──────────────┬──────────────┘
                                     ▼
                          ┌─────────────────────┐
                          │ EVIDENCE LEDGER     │
                          │ SHA-256 hash chain  │
                          └──────────┬──────────┘
                                     ▼
                          ┌─────────────────────┐
                          │ FORENSIC REPORTING  │
                          └─────────────────────┘
```

## Technology stack

| Layer        | Technology                                  |
| ------------ | ------------------------------------------- |
| Frontend     | Next.js, TypeScript, Tailwind CSS, shadcn/ui |
| Graph        | React Flow                                  |
| Map          | Leaflet                                     |
| Charts       | Recharts                                    |
| Backend      | Python, FastAPI, Pydantic, SQLAlchemy       |
| Database     | PostgreSQL                                  |
| Queue/Cache  | Redis + Celery                              |
| Reports      | HTML-to-PDF pipeline (server-side)          |
| ML           | scikit-learn                                |
| Parsing      | Python standard-library email, dnspython, tldextract, rapidfuzz |

## Modules

- `backend/apps/forensics` — parser, headers, Received chain, auth
- `backend/apps/intelligence` — provider adapters, DNS/RDAP/reputation
- `backend/apps/risk` — findings engine, risk fusion
- `backend/apps/ml` — feature extraction, classifier
- `backend/apps/graph` — graph nodes/edges, correlation
- `backend/apps/ledger` — evidence hash chain, audit events
- `backend/apps/reports` — report generation
- `backend/apps/cases` — case management
- `backend/apps/auth` — auth/RBAC

## Deployment target

- Docker Compose for local development
- Stateless FastAPI workers behind Redis queue
- PostgreSQL as source of truth

## Design decisions v0

- Modular monolith, not microservices.
- Relational graph storage (`graph_nodes`, `graph_edges`), not Neo4j for MVP.
- Provider-agnostic intelligence adapters.
- Evidence-first, deterministic before ML, ML before LLM.
- Tamper-evident hash chain, not blockchain.

## Open questions

- Which HTML-to-PDF library to use (WeasyPrint, Playwright, ReportLab)?
- Celery vs RQ for MVP? Decision: Celery due to broader ecosystem and explicit job state tracking.
- File storage: local filesystem vs MinIO/object storage for demo? Decision: local filesystem with safe paths for MVP.
