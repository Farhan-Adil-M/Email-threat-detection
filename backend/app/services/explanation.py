import json
from uuid import UUID
from sqlalchemy.orm import Session
from app.models.finding import Finding
from app.models.risk_assessment import RiskAssessment

def explain_case(db: Session, case_id: UUID) -> dict:
    risk = db.query(RiskAssessment).filter(RiskAssessment.case_id == case_id).order_by(RiskAssessment.created_at.desc()).first()
    findings = db.query(Finding).filter(Finding.case_id == case_id).order_by(Finding.score_delta.desc()).all()
    if not risk:
        return {"executive_summary": "No risk assessment is available.", "why_suspicious": [], "key_evidence": [], "possible_attack_type": [], "investigative_next_steps": ["Run forensic analysis and risk assessment."], "limitations": ["Risk assessment unavailable."]}
    limitations = json.loads(risk.limitations_json)
    return {"executive_summary": f"The message has a {risk.risk_level} risk assessment with score {risk.risk_score}.", "why_suspicious": [f.title for f in findings[:5]], "key_evidence": [{"rule_id": f.rule_id, "evidence_refs": json.loads(f.evidence_refs)} for f in findings[:5]], "possible_attack_type": json.loads(risk.classification_json), "investigative_next_steps": ["Validate sender identity independently.", "Review URLs and infrastructure without actively visiting untrusted destinations."], "limitations": limitations + ["This explanation is generated only from stored structured evidence."]}
