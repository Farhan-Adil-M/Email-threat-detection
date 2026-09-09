# API Contract v0 — SIH 26106 SENTINEL

## Base URL

```text
/api/v1
```

## Authentication

- JWT access token in `Authorization: Bearer <token>` header.
- Server-side RBAC enforced on every endpoint.

## Common response envelope

```json
{
  "success": true,
  "data": {},
  "error": null,
  "meta": {
    "request_id": "...",
    "timestamp": "..."
  }
}
```

## Core endpoints (v0)

### Cases

```text
GET    /cases              list cases
POST   /cases              create case
GET    /cases/{id}         get case
PATCH  /cases/{id}         update case
GET    /cases/{id}/findings
GET    /cases/{id}/graph
GET    /cases/{id}/ledger
GET    /cases/{id}/ledger/verify
GET    /cases/{id}/report
POST   /cases/{id}/report
```

### Evidence / Ingestion

```text
POST   /evidence/upload    upload .eml or raw email
GET    /evidence/{id}      download/view evidence
GET    /evidence/{id}/hash verify SHA-256
```

### Analysis jobs

```text
POST   /jobs/{case_id}/analyze        start analysis
GET    /jobs/{job_id}                 job status
GET    /jobs/{case_id}                job history
```

### Intelligence

```text
GET    /intelligence/ip/{ip}
GET    /intelligence/domain/{domain}
GET    /intelligence/url              query param: url
```

### Reports

```text
GET    /reports/{case_id}.pdf
GET    /reports/{case_id}.json
```

## Job status contract

```json
{
  "case_id": "...",
  "evidence_id": "...",
  "job_id": "...",
  "stage": "INTELLIGENCE_ENRICHED",
  "status": "completed",
  "started_at": "...",
  "completed_at": "...",
  "warnings": [],
  "provider_failures": []
}
```

## Analysis stages

```text
INGESTED
PARSED
HEADER_ANALYZED
AUTH_ANALYZED
CONTENT_ANALYZED
INDICATORS_EXTRACTED
INTELLIGENCE_ENRICHED
ML_ANALYZED
RISK_COMPUTED
GRAPH_BUILT
CORRELATED
REPORT_READY
FAILED | PARTIAL | DEGRADED
```

## Key schemas

### Finding

```json
{
  "id": "...",
  "rule_id": "URL-LOOKALIKE-001",
  "category": "URL",
  "severity": "high",
  "title": "Potential lookalike domain",
  "description": "...",
  "evidence_refs": ["..."],
  "score_delta": 14,
  "confidence": 0.88,
  "status": "confirmed|suspected|informational"
}
```

### RiskAssessment

```json
{
  "risk_score": 88,
  "risk_level": "high",
  "confidence": 0.82,
  "classification": ["phishing", "impersonation"],
  "model_version": "baseline-001",
  "contributions": [],
  "limitations": []
}
```

## Versioning

- v0 is exploratory and will evolve.
- Prefer additive changes.
- Document breaking changes in `docs/decisions/`.

## Open questions

- Pagination defaults and max page size.
- WebSocket vs polling for job status.
- OpenAPI generation strategy.
