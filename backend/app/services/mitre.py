import json
from uuid import UUID
from sqlalchemy.orm import Session
from app.models.campaign import MitreMapping
from app.models.finding import Finding

def map_case(db: Session, case_id: UUID) -> list[MitreMapping]:
    findings = db.query(Finding).filter(Finding.case_id == case_id).all()
    mappings = []
    if any(f.category == "URL" for f in findings):
        mappings.append(MitreMapping(case_id=case_id, technique="T1566.002", reason="Evidence includes a suspicious link indicator.", evidence_refs=json.dumps([str(f.id) for f in findings if f.category == "URL"]), confidence=0.75))
    if any(f.category == "CONTENT" for f in findings):
        mappings.append(MitreMapping(case_id=case_id, technique="T1566", reason="Evidence includes phishing/social-engineering content indicators.", evidence_refs=json.dumps([str(f.id) for f in findings if f.category == "CONTENT"]), confidence=0.6))
    db.add_all(mappings); db.commit()
    return mappings
