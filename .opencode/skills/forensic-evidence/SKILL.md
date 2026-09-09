---
name: forensic-evidence
description: Use when implementing evidence hashing, audit events, hash chaining, or ledger verification. Maintain tamper-evident evidence integrity.
---

# Skill: Forensic Evidence

## Purpose

- SHA-256 evidence fingerprint
- Immutable-ish storage strategy
- Audit events
- Hash chaining
- Verification

## Rules

- Every mutation creates an audit event.
- Maintain previous/current hashes.
- Provide explicit verification endpoint.
- Do not call it a blockchain unless an actual blockchain is implemented.
- Call it: tamper-evident evidence ledger / hash chain.

## Evidence object

```text
id
type
hash
created_at
storage_reference
sensitivity
```

## Audit event

```text
event_id
actor
action
timestamp
case_id
evidence_refs
previous_hash
event_hash
metadata
```

## Hash chain

```text
event_hash = SHA256(canonical_event_payload + previous_hash)
```

Produces:

```text
GENESIS
  ↓
INGEST
  ↓
PARSE
  ↓
ANALYZE
  ↓
ENRICH
  ↓
REPORT
```

## Verification

Provide `GET /cases/{id}/ledger/verify`.

UI shows:

```text
Evidence Integrity
✓ Chain valid
✓ No broken links
✓ 12 events
```
