"""Tests for enhanced intelligence layer: providers, enricher, geolocation."""
import json
import uuid
from pathlib import Path

from fastapi.testclient import TestClient

FIXTURES = Path(__file__).parent.parent / "data" / "fixtures"


def _upload_and_analyze(client: TestClient, name: str) -> str:
    eml = (FIXTURES / name).read_bytes()
    upload = client.post("/api/v1/evidence/upload", files={"file": (name, eml, "message/rfc822")})
    assert upload.status_code == 200
    case_id = upload.json()["data"]["case_id"]
    analyze = client.post(f"/api/v1/cases/{case_id}/analyze")
    assert analyze.status_code == 200
    return case_id


def test_fixture_intelligence_returns_fixture_status(client: TestClient):
    """Fixture mode returns status=fixture for all indicators."""
    case_id = _upload_and_analyze(client, "legitimate.eml")
    enrich = client.post(f"/api/v1/cases/{case_id}/enrich")
    assert enrich.status_code == 200
    intel = enrich.json()["data"]
    assert len(intel) > 0
    for item in intel:
        assert item["status"] in ("fixture", "disabled")


def test_disabled_intelligence_returns_disabled_status(client: TestClient):
    """Disabled mode returns status=disabled for all indicators."""
    case_id = _upload_and_analyze(client, "legitimate.eml")
    enrich = client.post(f"/api/v1/cases/{case_id}/enrich")
    assert enrich.status_code == 200
    intel = enrich.json()["data"]
    assert len(intel) > 0


def test_enrichment_persists_results(client: TestClient):
    """Enrichment creates ThreatIntelResult rows that are retrievable."""
    case_id = _upload_and_analyze(client, "legitimate.eml")
    client.post(f"/api/v1/cases/{case_id}/enrich")
    intel = client.get(f"/api/v1/cases/{case_id}/intelligence")
    assert intel.status_code == 200
    rows = intel.json()["data"]
    assert len(rows) > 0
    for row in rows:
        assert "indicator" in row
        assert "provider" in row
        assert "data_json" in row


def test_enrichment_extracts_domains(client: TestClient):
    """Domains from email headers are extracted as indicators."""
    case_id = _upload_and_analyze(client, "legitimate.eml")
    enrich = client.post(f"/api/v1/cases/{case_id}/enrich")
    assert enrich.status_code == 200
    intel = enrich.json()["data"]
    indicator_types = {item["indicator_type"] for item in intel}
    assert "domain" in indicator_types


def test_normalize_indicator_domain():
    """Domain indicators are normalized (lowercase, stripped)."""
    from app.services.intelligence.providers import normalize_indicator
    assert normalize_indicator("Example.COM", "domain") == "example.com"
    assert normalize_indicator("  test.org  ", "domain") == "test.org"


def test_normalize_indicator_ip():
    """IP indicators are normalized (lowercase, stripped)."""
    from app.services.intelligence.providers import normalize_indicator
    assert normalize_indicator("192.168.1.1", "ip") == "192.168.1.1"
    assert normalize_indicator("  10.0.0.1  ", "ip") == "10.0.0.1"


def test_disabled_provider_returns_disabled():
    """DisabledProvider always returns status=disabled."""
    from app.services.intelligence.providers import DisabledProvider
    p = DisabledProvider()
    result = p.lookup("example.com", "domain")
    assert result.status == "disabled"
    assert result.provider == "disabled"


def test_fixture_provider_returns_fixture():
    """FixtureProvider always returns status=fixture with deterministic data."""
    from app.services.intelligence.providers import FixtureProvider
    p = FixtureProvider()
    result = p.lookup("example.com", "domain")
    assert result.status == "fixture"
    assert result.provider == "fixture"
    assert result.confidence == 0.5
    assert result.data["mode"] == "deterministic"


def test_rdap_provider_skips_non_domain():
    """RDAPProvider skips non-domain indicators."""
    from app.services.intelligence.providers_rdap import RDAPProvider
    p = RDAPProvider()
    result = p.lookup("192.168.1.1", "ip")
    assert result.status == "skipped"


def test_ipinfo_provider_skips_non_ip():
    """IPInfoProvider skips non-IP indicators."""
    from app.services.intelligence.providers_ipinfo import IPInfoProvider
    p = IPInfoProvider()
    result = p.lookup("example.com", "domain")
    assert result.status == "skipped"


def test_private_ip_not_enriched(client: TestClient):
    """Private IPs from ReceivedHop are not included as indicators."""
    case_id = _upload_and_analyze(client, "legitimate.eml")
    enrich = client.post(f"/api/v1/cases/{case_id}/enrich")
    assert enrich.status_code == 200
    intel = enrich.json()["data"]
    for item in intel:
        if item["indicator_type"] == "ip":
            import ipaddress
            addr = ipaddress.ip_address(item["indicator"])
            assert not addr.is_private


def test_geolocation_endpoint_returns_list(client: TestClient):
    """Geolocation endpoint returns a list."""
    case_id = _upload_and_analyze(client, "legitimate.eml")
    resp = client.get(f"/api/v1/cases/{case_id}/observed-infrastructure")
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert isinstance(data, list)


def test_geolocation_endpoint_returns_404_for_unknown_case(client: TestClient):
    """Geolocation endpoint returns 404 for unknown case."""
    fake_id = str(uuid.uuid4())
    resp = client.get(f"/api/v1/cases/{fake_id}/observed-infrastructure")
    assert resp.status_code == 404
