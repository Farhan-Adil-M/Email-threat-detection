"""Tests for enhanced case summary endpoint."""
import json
from pathlib import Path

from fastapi.testclient import TestClient

FIXTURES = Path(__file__).parent.parent / "data" / "fixtures"


def _upload_analyze_risk(client: TestClient, name: str) -> str:
    eml = (FIXTURES / name).read_bytes()
    upload = client.post("/api/v1/evidence/upload", files={"file": (name, eml, "message/rfc822")})
    case_id = upload.json()["data"]["case_id"]
    client.post(f"/api/v1/cases/{case_id}/analyze")
    client.post(f"/api/v1/cases/{case_id}/ml-analyze")
    client.post(f"/api/v1/cases/{case_id}/risk")
    return case_id


def test_summary_includes_received_hops(client: TestClient):
    """Summary includes structured hop data."""
    case_id = _upload_analyze_risk(client, "bec.eml")
    resp = client.get(f"/api/v1/cases/{case_id}/summary")
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert "hops" in data
    assert isinstance(data["hops"], list)
    if data["hops"]:
        hop = data["hops"][0]
        assert "source_host" in hop
        assert "source_ip" in hop
        assert "hop_index" in hop


def test_summary_includes_urls(client: TestClient):
    """Summary includes URL indicators."""
    case_id = _upload_analyze_risk(client, "credential_phishing.eml")
    resp = client.get(f"/api/v1/cases/{case_id}/summary")
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert "urls" in data
    assert isinstance(data["urls"], list)


def test_summary_includes_intelligence(client: TestClient):
    """Summary includes intelligence results after enrichment."""
    case_id = _upload_analyze_risk(client, "legitimate.eml")
    client.post(f"/api/v1/cases/{case_id}/enrich")
    resp = client.get(f"/api/v1/cases/{case_id}/summary")
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert "intelligence" in data
    assert isinstance(data["intelligence"], list)


def test_summary_includes_evidence_sha256(client: TestClient):
    """Summary includes evidence SHA-256 fingerprint."""
    case_id = _upload_analyze_risk(client, "bec.eml")
    resp = client.get(f"/api/v1/cases/{case_id}/summary")
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert "evidence_sha256" in data
    assert data["evidence_sha256"] is not None
    assert len(data["evidence_sha256"]) == 64


def test_summary_includes_attachments(client: TestClient):
    """Summary includes attachment metadata."""
    case_id = _upload_analyze_risk(client, "legitimate.eml")
    resp = client.get(f"/api/v1/cases/{case_id}/summary")
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert "attachments" in data
    assert isinstance(data["attachments"], list)


def test_summary_includes_campaign(client: TestClient):
    """Summary includes campaign data after correlation."""
    case_id = _upload_analyze_risk(client, "bec.eml")
    client.post(f"/api/v1/cases/{case_id}/correlate")
    resp = client.get(f"/api/v1/cases/{case_id}/summary")
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert "campaign" in data
    assert "related_case_ids" in data


def test_summary_includes_mitre(client: TestClient):
    """Summary includes MITRE mappings."""
    case_id = _upload_analyze_risk(client, "bec.eml")
    client.post(f"/api/v1/cases/{case_id}/mitre")
    resp = client.get(f"/api/v1/cases/{case_id}/summary")
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert "mitre" in data
    assert isinstance(data["mitre"], list)


def test_summary_includes_hops_count(client: TestClient):
    """Summary includes hops_count matching hops list length."""
    case_id = _upload_analyze_risk(client, "bec.eml")
    resp = client.get(f"/api/v1/cases/{case_id}/summary")
    data = resp.json()["data"]
    assert data["hops_count"] == len(data["hops"])


def test_summary_returns_404_for_unknown(client: TestClient):
    """Summary returns 404 for unknown case."""
    import uuid
    resp = client.get(f"/api/v1/cases/{uuid.uuid4()}/summary")
    assert resp.status_code == 404


def test_summary_email_has_reply_to_and_return_path(client: TestClient):
    """Summary email includes reply_to and return_path fields."""
    case_id = _upload_analyze_risk(client, "bec.eml")
    resp = client.get(f"/api/v1/cases/{case_id}/summary")
    data = resp.json()["data"]
    email = data["email"]
    assert "reply_to" in email
    assert "return_path" in email
