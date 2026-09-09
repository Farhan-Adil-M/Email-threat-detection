from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.errors import SentinelError
from app.core.auth import Principal, require_role
from app.database import get_db
from app.models.auth_result import AuthenticationResult
from app.models.evidence import EvidenceObject
from app.models.received_hop import ReceivedHop
from app.models.threat_intel import ThreatIntelResult
from app.models.case_note import CaseNote
from app.models.email import EmailMessage
from app.models.ml_assessment import MLAssessment
from app.schemas.common import (
    APIResponse,
    AnalyzeResponse,
    AuditEventRead,
    CaseCreate,
    CaseRead,
    FindingRead,
    LedgerVerifyResponse,
    ThreatIntelResultRead,
    MLAssessmentRead,
    RiskAssessmentRead, GraphRead, ExplanationRead,
    CampaignRead, MitreMappingRead,
    CaseUpdate, CaseNoteCreate, CaseNoteRead,
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
def list_cases(
    db: Session = Depends(get_db),
    page: int = 1,
    page_size: int = 20,
):
    service = CaseService(db)
    # Validate pagination params
    if page < 1:
        page = 1
    if page_size < 1 or page_size > 100:
        page_size = 20
    cases = service.list_cases(limit=page_size, offset=(page - 1) * page_size)
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


@router.patch("/{case_id}", response_model=APIResponse[CaseRead])
def update_case(case_id: str, payload: CaseUpdate, db: Session = Depends(get_db), principal: Principal = Depends(require_role("analyst", "admin"))):
    case_uuid = _parse_uuid(case_id)
    case = CaseService(db).get_case(case_uuid)
    if not case: raise SentinelError("Case not found", status_code=404)
    allowed_statuses = {"NEW", "TRIAGED", "INVESTIGATING", "CONTAINED", "RESOLVED", "FALSE_POSITIVE"}
    if payload.status and payload.status not in allowed_statuses: raise SentinelError("Invalid case status", status_code=400)
    for field in ("status", "severity", "tags"):
        value = getattr(payload, field)
        if value is not None: setattr(case, field, value)
    db.commit(); db.refresh(case)
    return APIResponse(data=case)


@router.get("/{case_id}/notes", response_model=APIResponse[list[CaseNoteRead]])
def list_notes(case_id: str, db: Session = Depends(get_db)):
    case_uuid = _parse_uuid(case_id)
    if not CaseService(db).get_case(case_uuid): raise SentinelError("Case not found", status_code=404)
    return APIResponse(data=db.query(CaseNote).filter(CaseNote.case_id == case_uuid).order_by(CaseNote.created_at.desc()).all())


@router.post("/{case_id}/notes", response_model=APIResponse[CaseNoteRead])
def add_note(case_id: str, payload: CaseNoteCreate, db: Session = Depends(get_db), principal: Principal = Depends(require_role("analyst", "admin"))):
    case_uuid = _parse_uuid(case_id)
    if not CaseService(db).get_case(case_uuid): raise SentinelError("Case not found", status_code=404)
    if not payload.body.strip(): raise SentinelError("Note body cannot be empty", status_code=400)
    note = CaseNote(case_id=case_uuid, author=principal.username, body=payload.body.strip())
    db.add(note); db.commit(); db.refresh(note)
    return APIResponse(data=note)


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


@router.post("/{case_id}/enrich", response_model=APIResponse[list[ThreatIntelResultRead]])
def enrich_case(case_id: str, db: Session = Depends(get_db)):
    case_uuid = _parse_uuid(case_id)
    if not CaseService(db).get_case(case_uuid):
        raise SentinelError("Case not found", status_code=404)
    from app.services.intelligence.enricher import IntelligenceEnricher

    results = IntelligenceEnricher(db).enrich_case(case_uuid)
    return APIResponse(data=results)


@router.get("/{case_id}/intelligence", response_model=APIResponse[list[ThreatIntelResultRead]])
def get_intelligence(case_id: str, db: Session = Depends(get_db)):
    case_uuid = _parse_uuid(case_id)
    if not CaseService(db).get_case(case_uuid):
        raise SentinelError("Case not found", status_code=404)
    results = db.query(ThreatIntelResult).filter(ThreatIntelResult.case_id == case_uuid).all()
    return APIResponse(data=results)


@router.post("/{case_id}/ml-analyze", response_model=APIResponse[MLAssessmentRead])
def ml_analyze_case(case_id: str, db: Session = Depends(get_db)):
    case_uuid = _parse_uuid(case_id)
    if not CaseService(db).get_case(case_uuid):
        raise SentinelError("Case not found", status_code=404)
    email = db.query(EmailMessage).filter(EmailMessage.case_id == case_uuid).order_by(EmailMessage.created_at.desc()).first()
    if not email:
        raise SentinelError("Run forensic analysis before ML analysis", status_code=400)
    from app.services.ml_baseline import classify_email
    import json

    result = classify_email(email.subject, email.body_text, email.from_address, email.reply_to)
    assessment = MLAssessment(
        case_id=case_uuid,
        email_id=email.id,
        model_version=result.model_version,
        phishing_probability=result.phishing_probability,
        bec_probability=result.bec_probability,
        impersonation_probability=result.impersonation_probability,
        important_features_json=json.dumps(result.important_features, sort_keys=True),
        limitations_json=json.dumps(result.limitations),
    )
    db.add(assessment)
    db.commit()
    db.refresh(assessment)
    return APIResponse(data=assessment)


@router.post("/{case_id}/risk", response_model=APIResponse[RiskAssessmentRead])
def risk_case(case_id: str, db: Session = Depends(get_db)):
    case_uuid = _parse_uuid(case_id)
    if not CaseService(db).get_case(case_uuid): raise SentinelError("Case not found", status_code=404)
    from app.services.risk_engine import RiskEngine
    return APIResponse(data=RiskEngine(db).assess(case_uuid))


@router.get("/{case_id}/explanation", response_model=APIResponse[ExplanationRead])
def explanation_case(case_id: str, db: Session = Depends(get_db)):
    case_uuid = _parse_uuid(case_id)
    if not CaseService(db).get_case(case_uuid): raise SentinelError("Case not found", status_code=404)
    from app.services.explanation import explain_case
    return APIResponse(data=explain_case(db, case_uuid))


@router.post("/{case_id}/graph", response_model=APIResponse[GraphRead])
def graph_case(case_id: str, db: Session = Depends(get_db)):
    case_uuid = _parse_uuid(case_id)
    if not CaseService(db).get_case(case_uuid): raise SentinelError("Case not found", status_code=404)
    from app.services.graph_builder import GraphBuilder
    nodes, edges = GraphBuilder(db).build(case_uuid)
    return APIResponse(data=GraphRead(nodes=nodes, edges=edges))


@router.post("/{case_id}/correlate", response_model=APIResponse[CampaignRead | None])
def correlate_case(case_id: str, db: Session = Depends(get_db)):
    case_uuid = _parse_uuid(case_id)
    if not CaseService(db).get_case(case_uuid): raise SentinelError("Case not found", status_code=404)
    from app.services.correlation import CorrelationService
    return APIResponse(data=CorrelationService(db).correlate(case_uuid))


@router.post("/{case_id}/mitre", response_model=APIResponse[list[MitreMappingRead]])
def mitre_case(case_id: str, db: Session = Depends(get_db)):
    case_uuid = _parse_uuid(case_id)
    if not CaseService(db).get_case(case_uuid): raise SentinelError("Case not found", status_code=404)
    from app.services.mitre import map_case
    return APIResponse(data=map_case(db, case_uuid))


@router.get("/{case_id}/report.json")
def report_json(case_id: str, db: Session = Depends(get_db)):
    case_uuid = _parse_uuid(case_id)
    if not CaseService(db).get_case(case_uuid): raise SentinelError("Case not found", status_code=404)
    from app.services.report_service import build_json_report
    return build_json_report(db, case_uuid)


@router.get("/{case_id}/report.pdf")
def report_pdf(case_id: str, db: Session = Depends(get_db)):
    from fastapi.responses import Response
    case_uuid = _parse_uuid(case_id)
    if not CaseService(db).get_case(case_uuid): raise SentinelError("Case not found", status_code=404)
    from app.services.report_service import build_pdf_report
    return Response(content=build_pdf_report(db, case_uuid), media_type="application/pdf", headers={"Content-Disposition": f"attachment; filename=sentinel-{case_id}.pdf"})


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
