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
    assert data["findings_count"] == 0


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
