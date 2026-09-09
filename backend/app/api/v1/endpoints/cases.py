from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.errors import SentinelError
from app.database import get_db
from app.models.auth_result import AuthenticationResult
from app.models.evidence import EvidenceObject
from app.models.received_hop import ReceivedHop
from app.schemas.common import (
    APIResponse,
    AnalyzeResponse,
    AuditEventRead,
    CaseCreate,
    CaseRead,
    FindingRead,
    LedgerVerifyResponse,
)
from app.services.audit_service import AuditService
from app.services.case_service import CaseService
from app.services.finding_service import FindingService
from app.services.forensics.pipeline import ForensicPipeline

router = APIRouter()


def _parse_uuid(case_id: str) -> UUID:
    try:
        return UUID(case_id)
    except ValueError:
        raise SentinelError("Invalid case_id format", status_code=400)


@router.get("", response_model=APIResponse[list[CaseRead]])
def list_cases(db: Session = Depends(get_db)):
    service = CaseService(db)
    cases = service.list_cases()
    return APIResponse(data=cases)


@router.post("", response_model=APIResponse[CaseRead])
def create_case(payload: CaseCreate, db: Session = Depends(get_db)):
    service = CaseService(db)
    case = service.create_case(payload)
    return APIResponse(data=case)


@router.get("/{case_id}", response_model=APIResponse[CaseRead])
def get_case(case_id: str, db: Session = Depends(get_db)):
    service = CaseService(db)
    case = service.get_case(_parse_uuid(case_id))
    if not case:
        raise SentinelError("Case not found", status_code=404)
    return APIResponse(data=case)


@router.post("/{case_id}/analyze", response_model=APIResponse[AnalyzeResponse])
def analyze_case(case_id: str, db: Session = Depends(get_db)):
    """Run forensic analysis on all raw email evidence in the case."""
    case_uuid = _parse_uuid(case_id)
    service = CaseService(db)
    case = service.get_case(case_uuid)
    if not case:
        raise SentinelError("Case not found", status_code=404)

    evidence_items = (
        db.query(EvidenceObject)
        .filter(EvidenceObject.case_id == case_uuid, EvidenceObject.type == "email_raw")
        .all()
    )
    if not evidence_items:
        raise SentinelError("No raw email evidence found for case", status_code=400)

    pipeline = ForensicPipeline(db)
    email_msg = None
    for evidence in evidence_items:
        email_msg = pipeline.analyze_evidence(evidence.id)

    if email_msg is None:
        raise SentinelError("Analysis produced no email message", status_code=500)

    finding_service = FindingService(db)
    findings = finding_service.list_for_email(email_msg.id)
    hops_count = (
        db.query(ReceivedHop).filter(ReceivedHop.email_id == email_msg.id).count()
    )
    auth_count = (
        db.query(AuthenticationResult)
        .filter(AuthenticationResult.email_id == email_msg.id)
        .count()
    )

    return APIResponse(
        data=AnalyzeResponse(
            case_id=case_uuid,
            email_id=email_msg.id,
            message_id=email_msg.message_id,
            findings_count=len(findings),
            hops_count=hops_count,
            auth_count=auth_count,
            status="analyzed",
            message="Forensic analysis completed.",
        )
    )


@router.get("/{case_id}/findings", response_model=APIResponse[list[FindingRead]])
def get_findings(case_id: str, db: Session = Depends(get_db)):
    case_uuid = _parse_uuid(case_id)
    service = CaseService(db)
    case = service.get_case(case_uuid)
    if not case:
        raise SentinelError("Case not found", status_code=404)

    finding_service = FindingService(db)
    findings = finding_service.list_for_case(case_uuid)
    return APIResponse(data=findings)


@router.get("/{case_id}/ledger", response_model=APIResponse[list[AuditEventRead]])
def get_ledger(case_id: str, db: Session = Depends(get_db)):
    service = AuditService(db)
    _, events = service.verify_chain(_parse_uuid(case_id))
    return APIResponse(data=events)


@router.get("/{case_id}/ledger/verify", response_model=APIResponse[LedgerVerifyResponse])
def verify_ledger(case_id: str, db: Session = Depends(get_db)):
    service = AuditService(db)
    valid, events = service.verify_chain(_parse_uuid(case_id))
    return APIResponse(
        data=LedgerVerifyResponse(
            valid=valid,
            event_count=len(events),
            events=events,
        )
    )
