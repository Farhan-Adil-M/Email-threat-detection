import hashlib
import json
from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.audit import AuditEvent


class AuditService:
    def __init__(self, db: Session):
        self.db = db

    def record(
        self,
        case_id: UUID,
        action: str,
        actor: str = "system",
        evidence_refs: list[str] | None = None,
        previous_hash: str | None = None,
        metadata: dict | None = None,
    ) -> AuditEvent:
        """Record a tamper-evident audit event.

        event_hash = SHA256(canonical_event_payload + previous_hash)
        """
        payload = {
            "case_id": str(case_id),
            "actor": actor,
            "action": action,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "evidence_refs": evidence_refs or [],
            "metadata": metadata or {},
        }
        canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
        event_hash = hashlib.sha256(
            (canonical + (previous_hash or "")).encode("utf-8")
        ).hexdigest()

        event = AuditEvent(
            case_id=case_id,
            actor=actor,
            action=action,
            evidence_refs=json.dumps(payload["evidence_refs"]),
            previous_hash=previous_hash,
            event_hash=event_hash,
            canonical_payload=canonical,
            metadata_json=json.dumps(metadata or {}),
        )
        self.db.add(event)
        self.db.commit()
        self.db.refresh(event)
        return event

    def get_previous_hash(self, case_id: UUID) -> str | None:
        """Return the event_hash of the most recent audit event for a case."""
        event = (
            self.db.query(AuditEvent)
            .filter(AuditEvent.case_id == case_id)
            .order_by(AuditEvent.timestamp.desc())
            .first()
        )
        return event.event_hash if event else None

    def verify_chain(self, case_id: UUID) -> tuple[bool, list[AuditEvent]]:
        """Verify the hash chain for a case."""
        events = (
            self.db.query(AuditEvent)
            .filter(AuditEvent.case_id == case_id)
            .order_by(AuditEvent.timestamp.asc())
            .all()
        )

        previous_hash = ""
        for event in events:
            expected = hashlib.sha256(
                (event.canonical_payload + (event.previous_hash or "")).encode("utf-8")
            ).hexdigest()
            if expected != event.event_hash:
                return False, events
            if previous_hash and event.previous_hash != previous_hash:
                return False, events
            previous_hash = event.event_hash

        return True, events
