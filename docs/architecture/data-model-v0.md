# Data Model v0 — SIH 26106 SENTINEL

## Source of truth

PostgreSQL. Graph data stored relationally.

## Core entities

```text
User
├── id
├── email
├── role (analyst | reviewer | admin)
├── created_at

Case
├── id
├── title
├── status (NEW | TRIAGED | INVESTIGATING | CONTAINED | RESOLVED | FALSE_POSITIVE)
├── severity
├── tags
├── created_by
├── created_at
├── updated_at

EvidenceObject
├── id
├── case_id
├── type (email_raw | email_message | attachment | header | report)
├── sha256
├── storage_reference
├── original_filename
├── sensitivity
├── created_at

EmailMessage
├── id
├── evidence_id
├── case_id
├── headers JSONB
├── from_address
├── to_addresses
├── cc_addresses
├── reply_to
├── return_path
├── subject
├── date
├── message_id
├── body_text
├── body_html_sanitized
├── created_at

ReceivedHop
├── id
├── email_id
├── hop_index
├── source_host
├── source_ip
├── destination_host
├── timestamp
├── protocol
├── is_private_ip

AuthenticationResult
├── id
├── email_id
├── mechanism (SPF | DKIM | DMARC)
├── domain
├── result
├── alignment
├── policy
├── explanation

Domain
├── id
├── name
├── punycode_name
├── created_at

IPAddress
├── id
├── address
├── is_private
├── asn_id
├── created_at

URL
├── id
├── raw
├── normalized
├── scheme
├── hostname
├── port
├── path
├── query
├── ip_literal
├── has_userinfo
├── created_at

Attachment
├── id
├── email_id
├── filename
├── content_type
├── size
├── sha256
├── metadata_only

ThreatIntelResult
├── id
├── indicator
├── indicator_type
├── provider
├── status
├── queried_at
├── data JSONB
├── confidence
├── source_reference

Finding
├── id
├── case_id
├── email_id
├── rule_id
├── category
├── severity
├── title
├── description
├── evidence_refs
├── score_delta
├── confidence
├── status

RiskAssessment
├── id
├── case_id
├── email_id
├── risk_score
├── risk_level
├── confidence
├── classification
├── model_version
├── contributions JSONB
├── limitations JSONB

Indicator
├── id
├── case_id
├── type
├── value
├── first_seen
├── last_seen

Campaign
├── id
├── name
├── description
├── confidence

CampaignMembership
├── id
├── campaign_id
├── case_id
├── confidence
├── evidence_refs

GraphNode
├── id
├── case_id
├── node_type
├── label
├── entity_id
├── properties JSONB

GraphEdge
├── id
├── case_id
├── source_node_id
├── target_node_id
├── relationship_type
├── confidence
├── evidence_refs
├── created_at

AuditEvent
├── id
├── case_id
├── actor
├── action
├── timestamp
├── evidence_refs
├── previous_hash
├── event_hash
├── metadata JSONB

EvidenceLedgerEntry
├── id
├── case_id
├── event_id
├── entry_type
├── sha256
├── previous_hash
├── created_at

Report
├── id
├── case_id
├── format (pdf | json)
├── storage_reference
├── generated_by
├── created_at
```

## Notes

- JSONB used for flexible evidence containers where schema stability is low.
- Evidence refs stored as arrays of EvidenceObject IDs.
- All mutations produce AuditEvent and update hash chain.
- Graph is case-scoped; cross-case correlation requires explicit Campaign or shared indicator logic.

## Open questions

- Exact indexing strategy for graph lookups.
- Retention policy table design.
