# MVP Scope — SIH 26106 SENTINEL

## Goal

Deliver a technically credible, explainable, demoable email forensic investigation platform for SIH 26106.

## In-scope for MVP

### S-TIER (must work)

1. Email upload (.eml and raw/header paste)
2. Secure evidence hash (SHA-256)
3. RFC-aware parser
4. Header forensics and Received chain
5. SPF / DKIM / DMARC analysis
6. URL / domain analysis
7. Deterministic findings engine
8. Explainable risk engine
9. IP / domain intelligence with graceful degradation
10. Investigation graph
11. Case management
12. Tamper-evident evidence ledger
13. Forensic report (PDF + JSON)
14. Investigation UI

### A-TIER (then add)

15. ML baseline classifier
16. Campaign correlation
17. MITRE ATT&CK mapping
18. Geo map view
19. LLM explanation layer
20. STIX-style export

### B-TIER (future)

21. Mailbox integration
22. SIEM integrations
23. Org-wide alerting
24. Real-time ingestion
25. Threat hunting

## Demo flow target (2–4 minutes)

1. Open dashboard.
2. Open/upload BEC fixture.
3. Show analysis pipeline completing.
4. Show HIGH RISK / BEC classification.
5. Expand risk evidence breakdown.
6. Show header route.
7. Show infrastructure map.
8. Open investigation graph.
9. Show related case / campaign.
10. Verify evidence chain.
11. Generate report.

## Fixtures

- Fixture A — Legitimate (expected LOW)
- Fixture B — CEO impersonation / BEC (expected HIGH/CRITICAL)
- Fixture C — Credential phishing (expected HIGH/CRITICAL)
- Fixture D — Campaign (expected possible campaign relationship)

## Non-goals for MVP

- Full blockchain network
- Kubernetes / microservices
- Custom LLM
- Giant vector database
- Mobile app
- Browser extension
- Real-time mailbox ingestion
- Malware execution

## Success criteria

- Fresh install works
- Backend and frontend start
- Fixtures load
- Full pipeline from upload to report works
- Security tests pass
- E2E demo completes without manual database surgery
