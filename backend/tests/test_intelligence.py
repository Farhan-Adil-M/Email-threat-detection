from pathlib import Path

from fastapi.testclient import TestClient

from app.config import settings


FIXTURES = Path(__file__).parent.parent / "data" / "fixtures"


def test_fixture_intelligence_is_labeled_and_persisted(client: TestClient):
    old_mode = settings.INTEL_MODE
    settings.INTEL_MODE = "fixture"
    try:
        upload = client.post(
            "/api/v1/evidence/upload",
            files={
                "file": (
                    "credential_phishing.eml",
                    (FIXTURES / "credential_phishing.eml").read_bytes(),
                    "message/rfc822",
                )
            },
        )
        case_id = upload.json()["data"]["case_id"]
        client.post(f"/api/v1/cases/{case_id}/analyze")
        enriched = client.post(f"/api/v1/cases/{case_id}/enrich")
        assert enriched.status_code == 200
        results = enriched.json()["data"]
        assert results
        assert all(item["status"] == "fixture" for item in results)
        listed = client.get(f"/api/v1/cases/{case_id}/intelligence")
        assert len(listed.json()["data"]) == len(results)
    finally:
        settings.INTEL_MODE = old_mode


def test_disabled_intelligence_is_explicit(client: TestClient):
    old_mode = settings.INTEL_MODE
    settings.INTEL_MODE = "disabled"
    try:
        upload = client.post(
            "/api/v1/evidence/upload",
            files={
                "file": (
                    "legitimate.eml",
                    (FIXTURES / "legitimate.eml").read_bytes(),
                    "message/rfc822",
                )
            },
        )
        case_id = upload.json()["data"]["case_id"]
        client.post(f"/api/v1/cases/{case_id}/analyze")
        results = client.post(f"/api/v1/cases/{case_id}/enrich").json()["data"]
        assert results
        assert all(item["status"] == "disabled" for item in results)
    finally:
        settings.INTEL_MODE = old_mode
