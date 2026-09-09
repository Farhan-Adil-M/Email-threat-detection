import uuid

from sqlalchemy.orm import Session

from app.models.case import Case
from app.schemas.common import CaseCreate


class CaseService:
    def __init__(self, db: Session):
        self.db = db

    def list_cases(self) -> list[Case]:
        return self.db.query(Case).order_by(Case.created_at.desc()).all()

    def create_case(self, payload: CaseCreate) -> Case:
        case = Case(
            id=uuid.uuid4(),
            title=payload.title,
            tags=payload.tags,
            created_by="system",
        )
        self.db.add(case)
        self.db.commit()
        self.db.refresh(case)
        return case

    def get_case(self, case_id: str) -> Case | None:
        return self.db.query(Case).filter(Case.id == case_id).first()
