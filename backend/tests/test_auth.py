from pathlib import Path

from fastapi.testclient import TestClient

FIXTURES = Path(__file__).parent.parent / "data" / "fixtures"


def _read_fixture(name: str) -> bytes:
    return (FIXTURES / name).read_bytes()


def _upload_and_analyze(client: TestClient, name: str) -> tuple[str, list[dict]]:
    eml = _read_fixture(name)
    upload = client.post(
        "/api/v1/evidence/upload",
        files={"file": (name, eml, "message/rfc822")},
    )
    assert upload.status_code == 200
    case_id = upload.json()["data"]["case_id"]

    analyze = client.post(f"/api/v1/cases/{case_id}/analyze")
    assert analyze.status_code == 200

    findings = client.get(f"/api/v1/cases/{case_id}/findings")
    assert findings.status_code == 200
    return case_id, findings.json()["data"]


def test_spf_fail_finding(client: TestClient):
    _, items = _upload_and_analyze(client, "auth_spf_fail.eml")
    rule_ids = {f["rule_id"] for f in items}
    assert "AUTH-SPF-FAIL-001" in rule_ids
    dmarc_finding = next(f for f in items if f["rule_id"] == "AUTH-SPF-FAIL-001")
    assert dmarc_finding["severity"] == "high"


def test_dkim_fail_finding(client: TestClient):
    _, items = _upload_and_analyze(client, "auth_dkim_fail.eml")
    rule_ids = {f["rule_id"] for f in items}
    assert "AUTH-DKIM-FAIL-001" in rule_ids


def test_dmarc_fail_finding(client: TestClient):
    _, items = _upload_and_analyze(client, "auth_dmarc_fail.eml")
    rule_ids = {f["rule_id"] for f in items}
    assert "AUTH-DMARC-FAIL-001" in rule_ids
    dmarc_finding = next(f for f in items if f["rule_id"] == "AUTH-DMARC-FAIL-001")
    assert dmarc_finding["severity"] == "high"
    assert "REJECT" in dmarc_finding["description"]


def test_all_auth_pass_no_fail_findings(client: TestClient):
    _, items = _upload_and_analyze(client, "auth_all_pass.eml")
    auth_fail_rules = {
        f["rule_id"]
        for f in items
        if f["rule_id"].startswith("AUTH-") and "FAIL" in f["rule_id"]
    }
    assert not auth_fail_rules


def test_missing_auth_header(client: TestClient):
    _, items = _upload_and_analyze(client, "auth_missing.eml")
    rule_ids = {f["rule_id"] for f in items}
    assert "AUTH-MISSING-001" in rule_ids
