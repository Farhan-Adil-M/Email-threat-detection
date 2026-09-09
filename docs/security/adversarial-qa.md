# Adversarial QA Coverage

Covered fixtures include:

- malformed/missing headers
- malformed Received chain
- path traversal filename
- oversized upload
- invalid MIME type
- HTML link extraction
- userinfo/IP-literal/unusual-port URLs
- missing and failing SPF/DKIM/DMARC
- metadata-only attachment handling

The parser never executes attachments and active URL fetching is not implemented.
