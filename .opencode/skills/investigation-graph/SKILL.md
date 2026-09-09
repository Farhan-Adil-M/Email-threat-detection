---
name: investigation-graph
description: Use when modeling investigation nodes/edges, relationship confidence, or case/campaign correlation. Graph edges require evidence.
---

# Skill: Investigation Graph

## Purpose

- Node/edge modeling
- Relationship confidence
- Case/campaign correlation

## Rules

- Graph edges require evidence.
- No unsupported "confirmed" relationships.
- Distinguish observed relationship from inferred relationship.
- Preserve evidence references on every edge.

## Node types

```text
Email
Sender
Recipient
Domain
IP
URL
AttachmentHash
ASN
Case
Campaign
```

## Edge types

```text
SENT_FROM
REPLY_TO
CONTAINS_URL
RESOLVES_TO
HOSTED_ON
APPEARS_IN
RELATED_TO
SAME_INFRASTRUCTURE
SHARES_INDICATOR
MEMBER_OF_CAMPAIGN
```

## Edge contract

```text
relationship_type
confidence
evidence_refs
created_at
```

## Correlation

When cases share IP, domain, URL, attachment hash, related domain, sender infrastructure, or repeated pattern, show "Possible campaign relationship."
Never automatically show "Confirmed campaign" unless evidence is strong.

## Wow moment

Click Email → sender domain → suspicious URL → resolved IP → ASN → previous case → campaign.
Side panel shows why the relationship exists, evidence, first/last observed, and confidence.
