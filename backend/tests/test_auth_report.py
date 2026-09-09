from pathlib import Path

def test_login_and_report_json(client):
    login = client.post("/api/v1/auth/login", json={"username": "analyst", "password": "change-me-analyst"})
    assert login.status_code == 200
    assert login.json()["data"]["access_token"]
    fixture = Path(__file__).parent.parent / "data/fixtures/bec.eml"
    upload = client.post("/api/v1/evidence/upload", files={"file": ("bec.eml", fixture.read_bytes(), "message/rfc822")})
    case_id = upload.json()["data"]["case_id"]
    assert client.post(f"/api/v1/cases/{case_id}/analyze").status_code == 200
    report = client.get(f"/api/v1/cases/{case_id}/report.json")
    assert report.status_code == 200
    assert report.json()["case"]["id"] == case_id


def test_invalid_login_rejected(client):
    assert client.post("/api/v1/auth/login", json={"username": "analyst", "password": "wrong"}).status_code == 401
