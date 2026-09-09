import json
from uuid import UUID
from sqlalchemy.orm import Session
from app.models.case import Case
from app.models.email import EmailMessage
from app.models.finding import Finding
from app.models.risk_assessment import RiskAssessment
from app.models.threat_intel import ThreatIntelResult

def build_json_report(db: Session, case_id: UUID) -> dict:
    case = db.query(Case).filter(Case.id == case_id).first()
    email = db.query(EmailMessage).filter(EmailMessage.case_id == case_id).order_by(EmailMessage.created_at.desc()).first()
    findings = db.query(Finding).filter(Finding.case_id == case_id).all()
    risk = db.query(RiskAssessment).filter(RiskAssessment.case_id == case_id).order_by(RiskAssessment.created_at.desc()).first()
    intel = db.query(ThreatIntelResult).filter(ThreatIntelResult.case_id == case_id).all()
    return {
        "case": {"id": str(case.id), "title": case.title, "status": case.status, "severity": case.severity} if case else None,
        "analysis_status": "completed" if email else "not_analyzed",
        "email_identity": {"from": email.from_address, "reply_to": email.reply_to, "subject": email.subject, "message_id": email.message_id} if email else None,
        "risk": {"score": risk.risk_score, "level": risk.risk_level, "confidence": risk.confidence, "model_version": risk.model_version, "contributions": json.loads(risk.contributions_json), "limitations": json.loads(risk.limitations_json)} if risk else None,
        "findings": [{"rule_id": f.rule_id, "category": f.category, "severity": f.severity, "title": f.title, "description": f.description, "evidence_refs": json.loads(f.evidence_refs)} for f in findings],
        "intelligence": [{"indicator": x.indicator, "provider": x.provider, "status": x.status, "confidence": x.confidence, "source_reference": x.source_reference} for x in intel],
        "limitations": ["Infrastructure intelligence is optional enrichment.", "IP/domain observations do not establish physical attacker identity."],
    }
