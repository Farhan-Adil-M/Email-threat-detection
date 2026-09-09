import json
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.email import EmailMessage
from app.models.graph import GraphEdge, GraphNode
from app.models.url_indicator import URLIndicator


class GraphBuilder:
    def __init__(self, db: Session): self.db = db

    def build(self, case_id: UUID) -> tuple[list[GraphNode], list[GraphEdge]]:
        email = self.db.query(EmailMessage).filter(EmailMessage.case_id == case_id).order_by(EmailMessage.created_at.desc()).first()
        if not email: return [], []
        nodes: list[GraphNode] = []
        edges: list[GraphEdge] = []
        email_node = GraphNode(case_id=case_id, node_type="Email", label=email.subject or email.message_id or "Email", entity_id=str(email.id), properties_json=json.dumps({"message_id": email.message_id}))
        self.db.add(email_node); self.db.flush(); nodes.append(email_node)
        if email.from_address:
            sender = email.from_address.rsplit("@", 1)[-1]
            domain = GraphNode(case_id=case_id, node_type="Domain", label=sender, entity_id=sender, properties_json="{}")
            self.db.add(domain); self.db.flush(); nodes.append(domain)
            edge = GraphEdge(case_id=case_id, source_node_id=email_node.id, target_node_id=domain.id, relationship_type="SENT_FROM", confidence=1.0, evidence_refs=json.dumps([str(email.id)]))
            self.db.add(edge); edges.append(edge)
        for url in self.db.query(URLIndicator).filter(URLIndicator.case_id == case_id).all():
            url_node = GraphNode(case_id=case_id, node_type="URL", label=url.normalized_url, entity_id=str(url.id), properties_json=json.dumps({"hostname": url.hostname}))
            self.db.add(url_node); self.db.flush(); nodes.append(url_node)
            edge = GraphEdge(case_id=case_id, source_node_id=email_node.id, target_node_id=url_node.id, relationship_type="CONTAINS_URL", confidence=1.0, evidence_refs=json.dumps([str(url.id)]))
            self.db.add(edge); edges.append(edge)
        self.db.commit()
        return nodes, edges
