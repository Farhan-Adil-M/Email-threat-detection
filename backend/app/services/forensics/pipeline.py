import json
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.auth_result import AuthenticationResult
from app.models.email import EmailMessage
from app.models.evidence import EvidenceObject
from app.models.received_hop import ReceivedHop
from app.services.audit_service import AuditService
from app.services.finding_service import FindingService
from app.services.forensics.auth_analyzer import parse_authentication_results
from app.services.forensics.header_analyzer import analyze_headers
from app.services.forensics.parser import parse_email_bytes
from app.services.forensics.received_chain import parse_received_chain
from app.services.storage_service import StorageService


class ForensicPipeline:
    def __init__(self, db: Session):
        self.db = db

    def analyze_evidence(self, evidence_id: UUID) -> EmailMessage:
        """Run the full forensic pipeline on an evidence object."""
        evidence = self.db.query(EvidenceObject).filter(EvidenceObject.id == evidence_id).first()
        if not evidence:
            raise ValueError("Evidence not found")

        storage = StorageService()
        raw_bytes = storage.read_by_hash(evidence.sha256)
        if raw_bytes is None:
            raise ValueError("Evidence content missing from storage")

        parsed = parse_email_bytes(raw_bytes)

        # Create EmailMessage
        email_msg = EmailMessage(
            evidence_id=evidence.id,
            case_id=evidence.case_id,
            from_address=parsed.from_address,
            from_display_name=parsed.from_display_name,
            to_addresses=json.dumps(parsed.to_addresses),
            cc_addresses=json.dumps(parsed.cc_addresses),
            reply_to=parsed.reply_to,
            return_path=parsed.return_path,
            subject=parsed.subject,
            date=parsed.date,
            message_id=parsed.message_id,
            body_text=parsed.body_text,
            body_html_sanitized=parsed.body_html_sanitized,
            raw_headers=parsed.raw_headers,
        )
        self.db.add(email_msg)
        self.db.flush()  # Get email_msg.id

        # Received chain
        hops = parse_received_chain(parsed.received)
        for idx, hop in enumerate(hops):
            self.db.add(
                ReceivedHop(
                    email_id=email_msg.id,
                    case_id=evidence.case_id,
                    hop_index=idx,
                    raw_value=hop.raw,
                    source_host=hop.source_host,
                    source_ip=hop.source_ip,
                    destination_host=hop.destination_host,
                    protocol=hop.protocol,
                    timestamp=hop.timestamp,
                    is_private_ip=hop.is_private_ip,
                    is_malformed=hop.is_malformed,
                    missing_data=hop.missing_data,
                )
            )

        # Authentication results
        auth_records = parse_authentication_results(parsed.authentication_results)
        for record in auth_records:
            self.db.add(
                AuthenticationResult(
                    email_id=email_msg.id,
                    case_id=evidence.case_id,
                    mechanism=record.mechanism,
                    domain=record.domain,
                    result=record.result,
                    alignment=record.alignment,
                    policy=record.policy,
                    explanation=record.explanation,
                    raw_result=record.raw_result,
                )
            )

        # Header / content findings
        findings = analyze_headers(
            from_address=parsed.from_address,
            from_display_name=parsed.from_display_name,
            reply_to=parsed.reply_to,
            return_path=parsed.return_path,
            subject=parsed.subject,
            body_text=parsed.body_text,
        )
        finding_service = FindingService(self.db)
        for finding in findings:
            finding_service.create_from_header_finding(
                case_id=evidence.case_id,
                email_id=email_msg.id,
                finding=finding,
            )

        self.db.commit()
        self.db.refresh(email_msg)

        # Audit event
        audit = AuditService(self.db)
        previous_hash = audit.get_previous_hash(evidence.case_id)
        audit.record(
            case_id=evidence.case_id,
            action="EMAIL_FORENSICS_COMPLETED",
            actor="system",
            evidence_refs=[str(evidence.id), str(email_msg.id)],
            previous_hash=previous_hash,
            metadata={
                "message_id": email_msg.message_id,
                "findings_count": len(findings),
                "hops_count": len(hops),
            },
        )

        return email_msg
