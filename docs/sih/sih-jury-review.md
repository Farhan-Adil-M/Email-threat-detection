# SIH Jury Review — Pre-Final

## Strong points

- Evidence-first workflow instead of a single opaque score.
- RFC-aware parsing, authentication analysis, passive URL inspection, and hash-chain preservation.
- Offline/degraded intelligence modes are explicit and labeled.
- Risk contributions reference deterministic findings and model limitations.

## Honest limitations

- Live RDAP/reputation providers are extension points, not claimed live hits.
- Geolocation is limited to observed infrastructure and is unavailable without a configured provider.
- Baseline ML uses a tiny synthetic seed corpus; no performance claim is made.
- Attribution of a person or physical attacker location is not claimed.

## Likely objections and answers

1. **Why not only use an LLM?** Structured evidence remains the source of truth; ML/LLM are signals.
2. **Is this blockchain?** No. It is a tamper-evident SHA-256 audit ledger.
3. **Can URLs execute?** No. URLs are extracted and normalized; active fetching is not enabled.
4. **What happens offline?** Core parsing, rules, risk, graph, ledger, and reports still work.
5. **Can the IP locate the attacker?** No. It identifies observed infrastructure only.

## Four-minute demo

Dashboard → upload BEC fixture → analyze → findings/risk → graph → ledger verification → JSON/PDF report.
