from fastapi.testclient import TestClient


def build_eml_bytes() -> bytes:
    return b"""From: sender@example.com
To: victim@example.com
Subject: Test email
Message-ID: <test-123@example.com>
Date: Mon, 01 Jan 2024 00:00:00 +0000
MIME-Version: 1.0
Content-Type: text/plain

This is a test email body.
"""


def test_upload_creates_case_and_evidence(client: TestClient):
    eml = build_eml_bytes()
    response = client.post(
        "/api/v1/evidence/upload",
        files={"file": ("test.eml", eml, "message/rfc822")},
    )
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["sha256"]
    assert data["size"] == len(eml)
    assert data["filename"] == "test.eml"
    assert data["status"] == "ingested"


def test_upload_with_invalid_content_type(client: TestClient):
    response = client.post(
        "/api/v1/evidence/upload",
        files={"file": ("test.exe", b"MZ", "application/x-msdownload")},
    )
    assert response.status_code == 400


def test_upload_oversized_file(client: TestClient):
    # Build a file just over the 25 MB default limit.
    big = b"A" * (26 * 1024 * 1024)
    response = client.post(
        "/api/v1/evidence/upload",
        files={"file": ("big.eml", big, "message/rfc822")},
    )
    assert response.status_code == 413


def test_upload_path_traversal_filename(client: TestClient):
    eml = build_eml_bytes()
    response = client.post(
        "/api/v1/evidence/upload",
        files={"file": ("../../etc/passwd.eml", eml, "message/rfc822")},
    )
    assert response.status_code == 200
    data = response.json()["data"]
    assert ".." not in data["filename"]
    assert data["filename"].endswith(".eml")


def test_upload_existing_case(client: TestClient):
    eml = build_eml_bytes()
    # First upload creates a case
    r1 = client.post(
        "/api/v1/evidence/upload",
        files={"file": ("a.eml", eml, "message/rfc822")},
    )
    case_id = r1.json()["data"]["case_id"]

    # Second upload attaches to the same case
    r2 = client.post(
        "/api/v1/evidence/upload",
        data={"case_id": case_id},
        files={"file": ("b.eml", eml, "message/rfc822")},
    )
    assert r2.status_code == 200
    assert r2.json()["data"]["case_id"] == case_id


def test_upload_records_audit_event_and_verifies_ledger(client: TestClient):
    eml = build_eml_bytes()
    upload = client.post(
        "/api/v1/evidence/upload",
        files={"file": ("audit.eml", eml, "message/rfc822")},
    )
    assert upload.status_code == 200
    case_id = upload.json()["data"]["case_id"]
    sha256 = upload.json()["data"]["sha256"]

    verify = client.get(f"/api/v1/cases/{case_id}/ledger/verify")
    assert verify.status_code == 200
    data = verify.json()["data"]
    assert data["valid"] is True
    assert data["event_count"] == 1
    assert data["events"][0]["action"] == "EVIDENCE_INGESTED"
    assert sha256 in data["events"][0]["canonical_payload"]

    ledger = client.get(f"/api/v1/cases/{case_id}/ledger")
    assert ledger.status_code == 200
    assert len(ledger.json()["data"]) == 1
