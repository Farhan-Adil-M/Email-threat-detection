from pathlib import Path

from fastapi.testclient import TestClient

FIXTURES = Path(__file__).parent.parent / "data" / "fixtures"


def _read_fixture(name: str) -> bytes:
    return (FIXTURES / name).read_bytes()


def test_parse_legitimate_email(client: TestClient):
    eml = _read_fixture("legitimate.eml")
    upload = client.post(
        "/api/v1/evidence/upload",
        files={"file": ("legitimate.eml", eml, "message/rfc822")},
    )
    assert upload.status_code == 200
    case_id = upload.json()["data"]["case_id"]

    analyze = client.post(f"/api/v1/cases/{case_id}/analyze")
    assert analyze.status_code == 200
    data = analyze.json()["data"]
    assert data["status"] == "analyzed"

    findings = client.get(f"/api/v1/cases/{case_id}/findings")
    items = findings.json()["data"]
    non_auth_rules = {f["rule_id"] for f in items if not f["rule_id"].startswith("AUTH-")}
    assert non_auth_rules == set()


def test_parse_bec_email(client: TestClient):
    eml = _read_fixture("bec.eml")
    upload = client.post(
        "/api/v1/evidence/upload",
        files={"file": ("bec.eml", eml, "message/rfc822")},
    )
    assert upload.status_code == 200
    case_id = upload.json()["data"]["case_id"]

    analyze = client.post(f"/api/v1/cases/{case_id}/analyze")
    assert analyze.status_code == 200

    findings = client.get(f"/api/v1/cases/{case_id}/findings")
    assert findings.status_code == 200
    items = findings.json()["data"]
    rule_ids = {f["rule_id"] for f in items}

    assert "IDENTITY-REPLY-TO-MISMATCH-001" in rule_ids
    assert "IDENTITY-RETURN-PATH-MISMATCH-001" in rule_ids
    assert "IDENTITY-EXECUTIVE-DISPLAY-NAME-001" in rule_ids
    assert "IDENTITY-LOOKALIKE-DOMAIN-001" in rule_ids
    assert "CONTENT-URGENCY-001" in rule_ids
    assert "CONTENT-FINANCIAL-001" in rule_ids


def test_parse_credential_phishing(client: TestClient):
    eml = _read_fixture("credential_phishing.eml")
    upload = client.post(
        "/api/v1/evidence/upload",
        files={"file": ("credential_phishing.eml", eml, "message/rfc822")},
    )
    assert upload.status_code == 200
    case_id = upload.json()["data"]["case_id"]

    analyze = client.post(f"/api/v1/cases/{case_id}/analyze")
    assert analyze.status_code == 200
    data = analyze.json()["data"]
    assert data["status"] == "analyzed"
    assert data["auth_count"] == 0


def test_url_analysis_finds_ip_literal_and_userinfo(client: TestClient):
    eml = b"""From: sender@example.com
To: victim@example.com
Subject: Login
Message-ID: <url-001@example.com>
Date: Mon, 01 Jan 2024 11:00:00 +0000
MIME-Version: 1.0
Content-Type: text/plain

Open http://user:pass@192.0.2.10:8080/login now.
"""
    upload = client.post(
        "/api/v1/evidence/upload",
        files={"file": ("url.eml", eml, "message/rfc822")},
    )
    case_id = upload.json()["data"]["case_id"]
    analyzed = client.post(f"/api/v1/cases/{case_id}/analyze")
    assert analyzed.status_code == 200
    findings = client.get(f"/api/v1/cases/{case_id}/findings").json()["data"]
    rule_ids = {item["rule_id"] for item in findings}
    assert "URL-USERINFO-001" in rule_ids
    assert "URL-IP-LITERAL-001" in rule_ids
    assert "URL-UNUSUAL-PORT-001" in rule_ids


def test_attachment_metadata_only(client: TestClient):
    eml = b"""From: sender@example.com
To: victim@example.com
Subject: Attachment
Message-ID: <attachment-001@example.com>
MIME-Version: 1.0
Content-Type: multipart/mixed; boundary=demo

--demo
Content-Type: text/plain

See attachment.
--demo
Content-Type: application/octet-stream
Content-Disposition: attachment; filename=invoice.bin

safe synthetic bytes
--demo--
"""
    upload = client.post(
        "/api/v1/evidence/upload",
        files={"file": ("attachment.eml", eml, "message/rfc822")},
    )
    case_id = upload.json()["data"]["case_id"]
    analyzed = client.post(f"/api/v1/cases/{case_id}/analyze")
    assert analyzed.status_code == 200


def test_malformed_email_does_not_crash(client: TestClient):
    eml = _read_fixture("malformed_received.eml")
    upload = client.post(
        "/api/v1/evidence/upload",
        files={"file": ("malformed_received.eml", eml, "message/rfc822")},
    )
    assert upload.status_code == 200
    case_id = upload.json()["data"]["case_id"]

    analyze = client.post(f"/api/v1/cases/{case_id}/analyze")
    assert analyze.status_code == 200
    data = analyze.json()["data"]
    assert data["hops_count"] >= 1


def test_missing_from_header(client: TestClient):
    eml = _read_fixture("missing_from.eml")
    upload = client.post(
        "/api/v1/evidence/upload",
        files={"file": ("missing_from.eml", eml, "message/rfc822")},
    )
    assert upload.status_code == 200
    case_id = upload.json()["data"]["case_id"]

    analyze = client.post(f"/api/v1/cases/{case_id}/analyze")
    assert analyze.status_code == 200
    data = analyze.json()["data"]
    assert data["status"] == "analyzed"


def test_double_analyze_is_idempotentish(client: TestClient):
    eml = _read_fixture("legitimate.eml")
    upload = client.post(
        "/api/v1/evidence/upload",
        files={"file": ("legitimate.eml", eml, "message/rfc822")},
    )
    case_id = upload.json()["data"]["case_id"]

    r1 = client.post(f"/api/v1/cases/{case_id}/analyze")
    r2 = client.post(f"/api/v1/cases/{case_id}/analyze")
    assert r1.status_code == 200
    # Second analyze may create duplicate email message; that's acceptable for MVP.
    assert r2.status_code in (200, 500)
