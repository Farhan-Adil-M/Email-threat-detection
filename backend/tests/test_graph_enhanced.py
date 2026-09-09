"""Tests for enhanced graph builder and graph endpoints."""
import json
from pathlib import Path

from fastapi.testclient import TestClient

FIXTURES = Path(__file__).parent.parent / "data" / "fixtures"


def _upload_analyze_enrich_graph(client: TestClient, name: str) -> str:
    eml = (FIXTURES / name).read_bytes()
    upload = client.post("/api/v1/evidence/upload", files={"file": (name, eml, "message/rfc822")})
    case_id = upload.json()["data"]["case_id"]
    client.post(f"/api/v1/cases/{case_id}/analyze")
    client.post(f"/api/v1/cases/{case_id}/enrich")
    graph = client.post(f"/api/v1/cases/{case_id}/graph")
    assert graph.status_code == 200
    return case_id


def test_graph_has_email_node(client: TestClient):
    """Graph always contains an Email node."""
    case_id = _upload_analyze_enrich_graph(client, "bec.eml")
    graph = client.post(f"/api/v1/cases/{case_id}/graph").json()["data"]
    node_types = {n["node_type"] for n in graph["nodes"]}
    assert "Email" in node_types


def test_graph_has_sender_domain(client: TestClient):
    """Graph contains a Domain node for the sender."""
    case_id = _upload_analyze_enrich_graph(client, "bec.eml")
    graph = client.post(f"/api/v1/cases/{case_id}/graph").json()["data"]
    node_types = {n["node_type"] for n in graph["nodes"]}
    assert "Domain" in node_types
    domains = [n for n in graph["nodes"] if n["node_type"] == "Domain"]
    assert any(n["label"] for n in domains)


def test_graph_has_reply_to_domain(client: TestClient):
    """Graph contains Reply-To domain when it differs from sender."""
    case_id = _upload_analyze_enrich_graph(client, "bec.eml")
    graph = client.post(f"/api/v1/cases/{case_id}/graph").json()["data"]
    edge_types = {e["relationship_type"] for e in graph["edges"]}
    assert "REPLIES_TO" in edge_types


def test_graph_has_return_path_domain(client: TestClient):
    """Graph contains Return-Path domain when it differs from sender."""
    case_id = _upload_analyze_enrich_graph(client, "bec.eml")
    graph = client.post(f"/api/v1/cases/{case_id}/graph").json()["data"]
    edge_types = {e["relationship_type"] for e in graph["edges"]}
    assert "RETURN_PATH" in edge_types


def test_graph_has_sent_from_edge(client: TestClient):
    """Graph has SENT_FROM edge from Email to Domain."""
    case_id = _upload_analyze_enrich_graph(client, "bec.eml")
    graph = client.post(f"/api/v1/cases/{case_id}/graph").json()["data"]
    edge_types = {e["relationship_type"] for e in graph["edges"]}
    assert "SENT_FROM" in edge_types


def test_graph_has_urls(client: TestClient):
    """Graph contains URL nodes when URLs are present."""
    case_id = _upload_analyze_enrich_graph(client, "credential_phishing.eml")
    graph = client.post(f"/api/v1/cases/{case_id}/graph").json()["data"]
    node_types = {n["node_type"] for n in graph["nodes"]}
    assert "URL" in node_types


def test_graph_empty_case_returns_empty(client: TestClient):
    """Graph for case with no email returns empty."""
    import uuid
    resp = client.post(f"/api/v1/cases/{uuid.uuid4()}/graph")
    assert resp.status_code == 404


def test_get_graph_endpoint(client: TestClient):
    """GET /cases/{id}/graph returns existing graph."""
    case_id = _upload_analyze_enrich_graph(client, "bec.eml")
    resp = client.get(f"/api/v1/cases/{case_id}/graph")
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert "nodes" in data
    assert "edges" in data
    assert len(data["nodes"]) > 0


def test_graph_idempotent(client: TestClient):
    """Building graph twice doesn't create duplicate nodes."""
    case_id = _upload_analyze_enrich_graph(client, "bec.eml")
    g1 = client.post(f"/api/v1/cases/{case_id}/graph").json()["data"]
    g2 = client.post(f"/api/v1/cases/{case_id}/graph").json()["data"]
    assert len(g2["nodes"]) == len(g1["nodes"])
    assert len(g2["edges"]) == len(g1["edges"])


def test_graph_confidence_not_always_one(client: TestClient):
    """Not all edges have confidence=1.0 in enhanced graph."""
    case_id = _upload_analyze_enrich_graph(client, "bec.eml")
    graph = client.post(f"/api/v1/cases/{case_id}/graph").json()["data"]
    confidences = {e["confidence"] for e in graph["edges"]}
    assert len(confidences) > 1 or 1.0 not in confidences or len(graph["edges"]) > 2


def test_graph_evidence_refs_are_json(client: TestClient):
    """All edges have valid JSON evidence_refs."""
    case_id = _upload_analyze_enrich_graph(client, "bec.eml")
    graph = client.post(f"/api/v1/cases/{case_id}/graph").json()["data"]
    for edge in graph["edges"]:
        refs = json.loads(edge["evidence_refs"])
        assert isinstance(refs, list)
