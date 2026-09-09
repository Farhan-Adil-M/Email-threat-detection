---
name: threat-intelligence
description: Use when designing DNS, RDAP, ASN, geolocation, or reputation provider adapters. Enforces provider-agnostic interfaces, safe outbound requests, and provenance tracking.
---

# Skill: Threat Intelligence

## Purpose

- DNS, RDAP, IP enrichment
- Reputation provider adapters
- Cache / rate-limit / retry behavior
- Safe URL enrichment

## Rules

- Provider-agnostic interfaces first.
- Safe outbound requests: prevent SSRF, private/loopback/metadata IP leakage, DNS rebinding.
- Never depend on one provider.
- Minimize submitted data; extract only what the provider needs (IP, domain, URL, hash).
- Record provider, time, query, result provenance.
- Core analysis must continue when providers fail.

## Provider contract

Every adapter returns:

```json
{
  "provider": "provider-name",
  "status": "success",
  "queried_at": "...",
  "indicator": "...",
  "indicator_type": "ip|domain|url|hash",
  "data": {},
  "confidence": 0.0,
  "source_reference": "...",
  "raw_available": false
}
```

The analysis engine must never know vendor-specific response formats.

## Safety

- Explicit opt-in for active URL fetching.
- Sandboxed outbound requests.
- Strict allow/deny policy.
- Timeouts, redirect controls, private-IP blocking.
- No credential forwarding.
- Audit the action.
- Display that the URL was actively fetched.
