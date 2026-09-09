from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile
from sqlalchemy.orm import Session

from app.core.auth import _check_rate_limit, _get_client_ip, _upload_attempts
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


def _sniff_content_type(file_bytes: bytes) -> str:
    """Basic MIME type sniffing for email content."""
    if len(file_bytes) == 0:
        return "application/octet-stream"
    # Check for RFC822 email indicators
    if b"From:" in file_bytes[:1024] or b"To:" in file_bytes[:1024] or b"Subject:" in file_bytes[:1024]:
        return "message/rfc822"
    if file_bytes.startswith(b"%PDF"):
        return "application/pdf"
    if file_bytes.startswith(b"PK\x03\x04") or file_bytes.startswith(b"PK\x05\x06"):
        return "application/zip"
    return "application/octet-stream"


@router.post("/upload", response_model=APIResponse[UploadResponse])
def upload_evidence(
    request: Request,
    file: UploadFile = File(...),
    case_id: str | None = Form(None),
    db: Session = Depends(get_db),
):
    """Upload a .eml or raw email as evidence.

    If case_id is omitted, a new investigation case is created automatically.
    """
    client_ip = _get_client_ip(request)
    if not _check_rate_limit(_upload_attempts, f"upload:{client_ip}", 50, 300):
        raise HTTPException(status_code=429, detail="Too many upload attempts. Try again later.")

    # Read file content for validation
    content = file.file.read()
    file.file.seek(0)  # Reset for later reading

    # Size check
    if len(content) > 25 * 1024 * 1024:  # 25 MB
        raise HTTPException(status_code=413, detail="File exceeds maximum upload size")

    # MIME type validation - sniff content instead of trusting header
    sniffed_type = _sniff_content_type(content)
    allowed_types = {"message/rfc822", "text/plain"}
    if sniffed_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported content type: {sniffed_type}. Allowed: {', '.join(allowed_types)}",
        )

# Update file content type to sniffed type (read-only in Starlette, so we store it separately)
        # file.content_type = sniffed_type  # Not needed, we use sniffed_type for validation

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