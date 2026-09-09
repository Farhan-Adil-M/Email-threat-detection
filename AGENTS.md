# AGENTS.md — SIH 26106 SENTINEL

## Project identity

- **Problem Statement:** SIH 26106
- **Title:** AI-Powered Email Threat Detection, GeoLocation and Forensic Intelligence Platform
- **Product working name:** SENTINEL
- **Operating principle:** Detect → Explain → Trace → Correlate → Preserve → Report

## Source of truth

The build contract is `SIH-26106-GOATED-OpenCode-Build-Contract.md`. Every agent must read it before acting.

## Engineering rules

1. **Evidence before AI.** Structured deterministic evidence comes first. ML and LLM outputs are signals, not truth.
2. **Explain every score.** Every risk or confidence value must have a reproducible contribution breakdown.
3. **Never fake accuracy.** No fabricated metrics, benchmarks, threat-intel hits, geolocation precision, or attribution confidence.
4. **Never overclaim attribution.** Distinguish observed infrastructure from physical attacker identity.
5. **External APIs are enrichment.** Core analysis must work without them.
6. **Uploaded email content is hostile.** Treat HTML, attachments, URLs, headers, and metadata as attacker-controlled.
7. **Modular monolith first.** Next.js + FastAPI + PostgreSQL + Redis/Celery. No unnecessary microservices.

## Agent roster

- `sih-orchestrator` — primary orchestrator, architecture, planning, dispatch, verification
- `researcher` — standards/docs/threat-intel research, no code edits
- `architecture-reviewer` — architecture, dependency, scalability, failure-mode critique
- `forensics-engineer` — email parsing, header forensics, Received chain, authentication analysis
- `threat-intel-engineer` — DNS/RDAP/ASN/geolocation/reputation provider adapters
- `ml-risk-engineer` — feature extraction, baseline classifier, calibration, explainability
- `backend-engineer` — FastAPI, database, workers, services, APIs, auth/RBAC
- `frontend-engineer` — investigation workspace, dashboard, graph, geo, reports
- `security-reviewer` — attack-surface analysis, no edits by default
- `qa-engineer` — unit, integration, security, e2e tests and adversarial fixtures
- `interface-reviewer` — visual/UX/accessibility review, no edits
- `sih-jury-reviewer` — evaluates the project like a SIH judge
- `integration-engineer` — subsystem integration, schema reconciliation, full-system verification

## Workflow

1. Load relevant skill(s) for the task at hand.
2. Write a task contract before delegating.
3. Parallelize only independent work.
4. Serial flow for schemas, API contracts, core pipeline, integration, security remediation.
5. Every implementation agent returns: STATUS, SCOPE, FILES TOUCHED, CONTRACTS CHANGED, TESTS RUN, TEST RESULTS, RISKS, OPEN QUESTIONS, NEXT ACTION.
6. Reviewers return actionable findings with attacker-controlled input, vulnerable path, sink, impact, severity, and remediation.
7. The orchestrator reconciles before proceeding.

## Implementation order

RECON → RESEARCH → ARCHITECTURE → DATA MODEL → API CONTRACT → FOUNDATION → INGESTION → PARSER → FORENSICS → INTELLIGENCE → RULES → RISK → ML → GRAPH → CORRELATION → LEDGER → REPORT → FRONTEND POLISH → SECURITY REVIEW → ADVERSARIAL QA → SIH JURY REVIEW → FINAL DEMO

## Definition of done

- Fresh install works
- Migrations work
- Backend and frontend start
- Fixtures load
- `.eml` upload, parsing, forensics, auth, URL/domain, IP enrichment, findings, risk score, graph, ledger, and report all work
- Security tests pass
- E2E demo works end-to-end from a clean state
- Documentation is synchronized

## Model routing (use exact IDs from `opencode models`)

- Orchestrator / integration: `opencode-go/gpt-5.6-luna`
- Deep reasoning / security / architecture: `opencode-go/kimi-k3`
- Routine implementation: `opencode-go/kimi-k2.7-code`
- Cheap research / tests: `opencode-go/deepseek-v4-flash`

## Failure recovery

If a subagent fails: reproduce, isolate, determine failure class, invoke systematic debugging, fix root cause, rerun targeted and integration tests, document architectural lessons.

## Critical reminders

- Do not build the landing page first.
- Do not skip research or documentation.
- Do not add technologies because they sound impressive.
- Keep one source of truth for schemas.
- Maintain a tamper-evident evidence ledger, not a blockchain claim.
- Preserve the distinction between observed fact, inference, probability, and conclusion.
