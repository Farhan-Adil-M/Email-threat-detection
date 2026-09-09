from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.errors import SentinelError
from app.database import get_db
from app.schemas.common import (
    APIResponse,
    AuditEventRead,
    CaseCreate,
    CaseRead,
    LedgerVerifyResponse,
)
from app.services.audit_service import AuditService
from app.services.case_service import CaseService

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
