from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.common import APIResponse, CaseCreate, CaseRead
from app.services.case_service import CaseService

router = APIRouter()


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
    case = service.get_case(case_id)
    return APIResponse(data=case)
