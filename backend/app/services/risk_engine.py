import json
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.finding import Finding
from app.models.ml_assessment import MLAssessment
from app.models.risk_assessment import RiskAssessment


def level(score: int) -> str:
    if score < 20: return "low"
    if score < 40: return "guarded"
    if score < 60: return "medium"
    if score < 80: return "high"
    return "critical"


class RiskEngine:
    def __init__(self, db: Session):
        self.db = db

    def assess(self, case_id: UUID) -> RiskAssessment:
        findings = self.db.query(Finding).filter(Finding.case_id == case_id).all()
        ml = self.db.query(MLAssessment).filter(MLAssessment.case_id == case_id).order_by(MLAssessment.created_at.desc()).first()
        contributions = [{"source": "deterministic", "rule_id": f.rule_id, "title": f.title, "score_delta": f.score_delta, "evidence_refs": f.evidence_refs} for f in findings]
        score = min(100, max(0, sum(f.score_delta for f in findings)))
        limitations = []
        classifications = []
        if ml:
            ml_value = max(ml.phishing_probability, ml.bec_probability, ml.impersonation_probability)
            ml_delta = round(10 * ml_value)
            score = min(100, score + ml_delta)
            contributions.append({"source": "ml", "model_version": ml.model_version, "score_delta": ml_delta, "probabilities": {"phishing": ml.phishing_probability, "bec": ml.bec_probability, "impersonation": ml.impersonation_probability}})
            if ml.phishing_probability >= 0.5: classifications.append("phishing")
            if ml.bec_probability >= 0.5: classifications.append("bec")
            if ml.impersonation_probability >= 0.5: classifications.append("impersonation")
        else:
            limitations.append("ML assessment unavailable; deterministic findings only.")
        confidence = min(0.99, 0.45 + min(0.45, len(findings) * 0.05) + (0.1 if ml else 0.0))
        if not findings: limitations.append("No deterministic findings were available.")
        assessment = RiskAssessment(case_id=case_id, email_id=(findings[0].email_id if findings else ml.email_id), risk_score=score, risk_level=level(score), confidence=round(confidence, 2), classification_json=json.dumps(sorted(set(classifications))), contributions_json=json.dumps(contributions, sort_keys=True), limitations_json=json.dumps(limitations), model_version=ml.model_version if ml else "deterministic-only-001")
        self.db.add(assessment)
        self.db.commit()
        self.db.refresh(assessment)
        return assessment
