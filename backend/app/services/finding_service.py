import json
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.finding import Finding
from app.services.forensics.header_analyzer import HeaderFinding
from app.services.rule_catalog import get_rule


class FindingService:
    def __init__(self, db: Session):
        self.db = db

    def create_from_header_finding(
        self,
        case_id: UUID,
        email_id: UUID,
        finding: HeaderFinding,
    ) -> Finding:
        # Keep rule metadata centralized. Unknown rules remain visible for
        # forward compatibility, but are marked informational rather than
        # silently receiving an invented score policy.
        definition = get_rule(finding.rule_id)
        if definition is None:
            finding.confidence = min(finding.confidence, 0.5)
        record = Finding(
            case_id=case_id,
            email_id=email_id,
            rule_id=finding.rule_id,
            category=finding.category,
            severity=finding.severity,
            title=finding.title,
            description=finding.description,
            evidence_refs=json.dumps(finding.evidence),
            score_delta=finding.score_delta,
            confidence=finding.confidence,
            status="confirmed",
        )
        self.db.add(record)
        return record

    def list_for_case(self, case_id: UUID) -> list[Finding]:
        return (
            self.db.query(Finding)
            .filter(Finding.case_id == case_id)
            .order_by(Finding.score_delta.desc())
            .all()
        )

    def list_for_email(self, email_id: UUID) -> list[Finding]:
        return (
            self.db.query(Finding)
            .filter(Finding.email_id == email_id)
            .order_by(Finding.score_delta.desc())
            .all()
        )
