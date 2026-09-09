import json
from pathlib import Path

from fastapi.testclient import TestClient


def test_baseline_returns_probabilities_and_limitations(client: TestClient):
    fixture = Path(__file__).parent.parent / "data/fixtures/bec.eml"
    upload = client.post("/api/v1/evidence/upload", files={"file": ("bec.eml", fixture.read_bytes(), "message/rfc822")})
    case_id = upload.json()["data"]["case_id"]
    assert client.post(f"/api/v1/cases/{case_id}/analyze").status_code == 200
    response = client.post(f"/api/v1/cases/{case_id}/ml-analyze")
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["model_version"] == "nb-baseline-001"
    assert 0 <= data["phishing_probability"] <= 1
    assert 0 <= data["bec_probability"] <= 1
    assert 0 <= data["impersonation_probability"] <= 1
    assert json.loads(data["limitations_json"])


def test_ml_requires_forensics_first(client: TestClient):
    response = client.post("/api/v1/cases", json={"title": "Unanalyzed case"})
    case_id = response.json()["data"]["id"]
    assert client.post(f"/api/v1/cases/{case_id}/ml-analyze").status_code == 400
