# Threat Model v0 — SIH 26106 SENTINEL

## Assumptions

- An attacker controls email content: headers, MIME, HTML, URLs, attachments, filenames.
- The platform processes hostile input uploaded by analysts.
- External intelligence providers are untrusted third parties.
- Analysts have varying privilege levels.

## Threat actors

- External attacker sending malicious email to analyze.
- Malicious insider analyst.
- External intelligence provider collecting submitted data.

## Threats and mitigations

| Threat                  | Input / Vector                              | Mitigation v0                                                                       |
| ----------------------- | ------------------------------------------- | ----------------------------------------------------------------------------------- |
| Malicious upload        | `.eml`, oversized file, bad MIME            | File size limit, MIME sanity check, safe temp handling, scan for parser bombs       |
| Path traversal          | Malicious filename                          | Sanitize filename, store by content hash, no user path in storage                   |
| XSS                     | HTML email body                             | Sanitize HTML before display, never render as active HTML                           |
| Template injection      | User content in reports                     | Use server-side templating with auto-escaping, validate variables                   |
| SSRF                    | URLs in email trigger outbound fetch        | Default passive analysis; active scan opt-in with private-IP block, timeout, audit  |
| Command injection       | Filename, header values                     | No shell execution; use Python stdlib; validate strings                             |
| Resource exhaustion     | Parser bombs, nested MIME, long headers     | Size limits, recursion limits, timeouts, streaming where possible                   |
| Secret leakage          | Logs, error messages                        | Do not log full bodies, API keys, or PII by default                                 |
| IDOR                    | Case access across tenants/analysts         | Server-side authorization, tenant/analyst scoping on every case access              |
| Privilege escalation    | Frontend role spoofing                      | Server-side RBAC only                                                               |
| Prompt injection        | Email text contains instructions            | Treat email content as data; system instructions structurally separate from content |
| Supply-chain            | Malicious dependency                        | Pin versions, audit dependencies, minimal external packages                         |
| Cross-tenant exposure   | Shared graph/correlation                    | Scope queries by authorized case set                                                |

## In-scope for v0

- Input validation and sanitization
- Safe file storage by hash
- HTML sanitization
- SSRF prevention for passive analysis
- Server-side authorization
- Audit logging

## Out-of-scope for v0 (future)

- Full sandboxed attachment detonation
- Real-time mailbox ingestion
- Hardware security modules
- Formal code signing

## Next actions

- Implement input validators before parser.
- Add security tests for adversarial fixture matrix.
- Run security review after Foundation phase.
