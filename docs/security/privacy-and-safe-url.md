# Privacy and Safe URL Policy

- Raw email content stays in local evidence storage by default.
- External providers receive indicators only, never full email bodies.
- Intelligence mode is `disabled` by default; fixture mode is explicitly labeled.
- URLs are extracted and normalized passively. The server never automatically visits them.
- Any future active scan must be opt-in, sandboxed, timeout-bounded, redirect-controlled, and audited.
- IP geolocation describes observed infrastructure, not an attacker identity or physical location.
- Logs must not contain full message bodies, credentials, API keys, or unnecessary PII.
