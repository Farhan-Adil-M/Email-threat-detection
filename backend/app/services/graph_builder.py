import json
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.attachment import Attachment
from app.models.campaign import Campaign, CampaignMembership, MitreMapping
from app.models.email import EmailMessage
from app.models.evidence import EvidenceObject
from app.models.finding import Finding
from app.models.graph import GraphEdge, GraphNode
from app.models.received_hop import ReceivedHop
from app.models.threat_intel import ThreatIntelResult
from app.models.url_indicator import URLIndicator


class GraphBuilder:
    def __init__(self, db: Session):
        self.db = db

    def build(self, case_id: UUID) -> tuple[list[GraphNode], list[GraphEdge]]:
        existing = self.db.query(GraphNode).filter(GraphNode.case_id == case_id).count()
        if existing > 0:
            self.db.query(GraphEdge).filter(GraphEdge.case_id == case_id).delete()
            self.db.query(GraphNode).filter(GraphNode.case_id == case_id).delete()
            self.db.flush()

        email = (
            self.db.query(EmailMessage)
            .filter(EmailMessage.case_id == case_id)
            .order_by(EmailMessage.created_at.desc())
            .first()
        )
        if not email:
            self.db.commit()
            return [], []

        nodes: list[GraphNode] = []
        edges: list[GraphEdge] = []
        node_map: dict[str, GraphNode] = {}

        def add_node(node_type: str, label: str, entity_id: str | None = None, props: dict | None = None) -> GraphNode:
            key = f"{node_type}:{entity_id or label}"
            if key in node_map:
                return node_map[key]
            node = GraphNode(
                case_id=case_id, node_type=node_type, label=label,
                entity_id=entity_id, properties_json=json.dumps(props or {}),
            )
            self.db.add(node)
            self.db.flush()
            node_map[key] = node
            nodes.append(node)
            return node

        def add_edge(source: GraphNode, target: GraphNode, rel: str, confidence: float, evidence: list[str]) -> GraphEdge:
            edge = GraphEdge(
                case_id=case_id, source_node_id=source.id, target_node_id=target.id,
                relationship_type=rel, confidence=confidence,
                evidence_refs=json.dumps(evidence),
            )
            self.db.add(edge)
            edges.append(edge)
            return edge

        email_node = add_node("Email", email.subject or email.message_id or "Email",
                              entity_id=str(email.id),
                              props={"message_id": email.message_id, "from": email.from_address})

        if email.from_address:
            sender_domain = email.from_address.rsplit("@", 1)[-1]
            domain_node = add_node("Domain", sender_domain, entity_id=sender_domain,
                                   props={"role": "sender"})
            add_edge(email_node, domain_node, "SENT_FROM", 1.0, [str(email.id)])

        if email.reply_to and "@" in email.reply_to:
            reply_domain = email.reply_to.rsplit("@", 1)[-1]
            if reply_domain != (email.from_address.rsplit("@", 1)[-1] if email.from_address else None):
                rt_node = add_node("Domain", reply_domain, entity_id=reply_domain,
                                   props={"role": "reply_to"})
                add_edge(email_node, rt_node, "REPLIES_TO", 0.9, [str(email.id)])

        if email.return_path and "@" in email.return_path:
            rp_domain = email.return_path.rsplit("@", 1)[-1]
            if rp_domain != (email.from_address.rsplit("@", 1)[-1] if email.from_address else None):
                rp_node = add_node("Domain", rp_domain, entity_id=rp_domain,
                                   props={"role": "return_path"})
                add_edge(email_node, rp_node, "RETURN_PATH", 0.8, [str(email.id)])

        for url in self.db.query(URLIndicator).filter(URLIndicator.case_id == case_id).all():
            url_node = add_node("URL", url.normalized_url, entity_id=str(url.id),
                                props={"hostname": url.hostname, "scheme": url.scheme})
            add_edge(email_node, url_node, "CONTAINS_URL", 1.0, [str(url.id)])
            if url.hostname:
                hostname_node = add_node("Domain", url.hostname, entity_id=url.hostname,
                                         props={"role": "url_host"})
                add_edge(url_node, hostname_node, "HOSTS_AT", 0.95, [str(url.id)])

        seen_ips: set[str] = set()
        for hop in (
            self.db.query(ReceivedHop)
            .filter(ReceivedHop.case_id == case_id, ReceivedHop.source_ip.is_not(None), ReceivedHop.is_private_ip == False)
            .all()
        ):
            if hop.source_ip in seen_ips:
                continue
            seen_ips.add(hop.source_ip)
            ip_node = add_node("IP", hop.source_ip, entity_id=hop.source_ip,
                               props={"host": hop.source_host, "protocol": hop.protocol})
            add_edge(email_node, ip_node, "OBSERVED_VIA", 0.85,
                     [str(email.id)])

            for domain_node in [n for n in nodes if n.node_type == "Domain"]:
                add_edge(domain_node, ip_node, "RESOLVES_TO", 0.6, [])

        for att in self.db.query(Attachment).filter(Attachment.case_id == case_id).all():
            att_node = add_node("Attachment", att.filename or "unnamed", entity_id=str(att.id),
                                props={"content_type": att.content_type, "size": att.size})
            add_edge(email_node, att_node, "HAS_ATTACHMENT", 1.0, [str(att.id)])
            if att.sha256:
                hash_node = add_node("EvidenceHash", att.sha256[:32], entity_id=att.sha256,
                                     props={"type": "attachment_sha256"})
                add_edge(att_node, hash_node, "FINGERPRINT", 1.0, [str(att.id)])

        evidence = (
            self.db.query(EvidenceObject)
            .filter(EvidenceObject.case_id == case_id)
            .first()
        )
        if evidence and evidence.sha256:
            ev_node = add_node("EvidenceHash", evidence.sha256[:32], entity_id=evidence.sha256,
                               props={"type": "email_sha256", "filename": evidence.original_filename})
            add_edge(email_node, ev_node, "FINGERPRINT", 1.0, [str(evidence.id)])

        for intel in (
            self.db.query(ThreatIntelResult)
            .filter(ThreatIntelResult.case_id == case_id, ThreatIntelResult.status == "success")
            .all()
        ):
            intel_node = add_node("IntelResult", f"{intel.provider}: {intel.indicator}",
                                  entity_id=str(intel.id),
                                  props={"provider": intel.provider, "indicator": intel.indicator,
                                         "type": intel.indicator_type, "confidence": intel.confidence})
            for target in [n for n in nodes if n.entity_id == intel.indicator]:
                add_edge(target, intel_node, "ENRICHED_WITH", intel.confidence, [str(intel.id)])

        membership = (
            self.db.query(CampaignMembership)
            .filter(CampaignMembership.case_id == case_id)
            .first()
        )
        if membership:
            campaign = self.db.query(Campaign).filter(Campaign.id == membership.campaign_id).first()
            if campaign:
                camp_node = add_node("Campaign", campaign.name, entity_id=str(campaign.id),
                                     props={"confidence": campaign.confidence,
                                            "description": campaign.description})
                add_edge(email_node, camp_node, "PART_OF_CAMPAIGN", membership.confidence,
                         json.loads(membership.evidence_refs) if membership.evidence_refs else [])

        for mapping in self.db.query(MitreMapping).filter(MitreMapping.case_id == case_id).all():
            mitre_node = add_node("MITRE", mapping.technique, entity_id=mapping.technique,
                                  props={"reason": mapping.reason, "confidence": mapping.confidence})
            add_edge(email_node, mitre_node, "MAPS_TO", mapping.confidence,
                     json.loads(mapping.evidence_refs) if mapping.evidence_refs else [])

        self.db.commit()
        return nodes, edges
