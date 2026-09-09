# ADR-002 — Provider-Agnostic Infrastructure Intelligence

## Status

Accepted

## Decision

Phase 8 uses a normalized provider contract and explicit `INTEL_MODE` values:

- `disabled`: no external lookup; results are labeled `disabled`.
- `fixture`: deterministic demo-safe results labeled `fixture`.
- `live`: keyless DNS lookups are enabled; provider failures remain isolated.

Active URL fetching, reputation submissions, and arbitrary outbound requests are not part of the MVP.

## Rationale

Core forensic analysis must work offline and without third-party APIs. Every result preserves provider, status, timestamp, indicator, confidence, and provenance. This prevents fixture data from being presented as live intelligence and preserves degraded behavior for unreliable networks.

## Future extension

RDAP, offline GeoIP/ASN, and opt-in reputation adapters can implement the same normalized contract without changing the pipeline or frontend response shape.
