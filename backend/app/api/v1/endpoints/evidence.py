from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, UploadFile
from sqlalchemy.orm import Session

from app.core.errors import SentinelError
from app.core.security import validate_upload
from app.database import get_db
from app.schemas.common import APIResponse, UploadResponse
from app.services.audit_service import AuditService
from app.services.case_service import CaseService
from app.services.storage_service import StorageService

router = APIRouter()


def _parse_case_id(case_id: str | None) -> UUID | None:
    if not case_id:
        return None
    try:
        return UUID(case_id)
    except ValueError:
        raise SentinelError("Invalid case_id format", status_code=400)


@router.post("/upload", response_model=APIResponse[UploadResponse])
def upload_evidence(
    file: UploadFile = File(...),
    case_id: str | None = Form(None),
    db: Session = Depends(get_db),
):
    """Upload a .eml or raw email as evidence.

    If case_id is omitted, a new investigation case is created automatically.
    """
    validate_upload(file)

    # Resolve or create case
    case_service = CaseService(db)
    parsed_case_id = _parse_case_id(case_id)
    if parsed_case_id:
        case = case_service.get_case(parsed_case_id)
        if not case:
            raise SentinelError("Case not found", status_code=404)
    else:
        case = case_service.create_case_from_upload(file.filename or "Uploaded evidence")

    # Persist evidence
    storage = StorageService()
    evidence = storage.store_upload(case.id, file)
    db.add(evidence)
    db.commit()
    db.refresh(evidence)

    # Audit event
    audit = AuditService(db)
    previous_hash = audit.get_previous_hash(case.id)
    audit.record(
        case_id=case.id,
        action="EVIDENCE_INGESTED",
        actor="analyst",
        evidence_refs=[str(evidence.id)],
        previous_hash=previous_hash,
        metadata={
            "sha256": evidence.sha256,
            "filename": evidence.original_filename,
            "size": evidence.size,
        },
    )

    return APIResponse(
        data=UploadResponse(
            case_id=case.id,
            evidence_id=evidence.id,
            sha256=evidence.sha256,
            filename=evidence.original_filename,
            size=evidence.size,
            status="ingested",
            message="Evidence uploaded and fingerprinted.",
        )
    )
