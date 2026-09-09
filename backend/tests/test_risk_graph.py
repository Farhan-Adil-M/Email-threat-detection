from pathlib import Path


def test_risk_explanation_and_graph_vertical_slice(client):
    fixture = Path(__file__).parent.parent / "data/fixtures/bec.eml"
    upload = client.post("/api/v1/evidence/upload", files={"file": ("bec.eml", fixture.read_bytes(), "message/rfc822")})
    case_id = upload.json()["data"]["case_id"]
    assert client.post(f"/api/v1/cases/{case_id}/analyze").status_code == 200
    assert client.post(f"/api/v1/cases/{case_id}/ml-analyze").status_code == 200
    risk = client.post(f"/api/v1/cases/{case_id}/risk")
    assert risk.status_code == 200
    risk_data = risk.json()["data"]
    assert 0 <= risk_data["risk_score"] <= 100
    assert risk_data["contributions_json"]
    explanation = client.get(f"/api/v1/cases/{case_id}/explanation")
    assert explanation.status_code == 200
    assert explanation.json()["data"]["key_evidence"]
    graph = client.post(f"/api/v1/cases/{case_id}/graph")
    assert graph.status_code == 200
    assert graph.json()["data"]["nodes"]
    assert graph.json()["data"]["edges"]
