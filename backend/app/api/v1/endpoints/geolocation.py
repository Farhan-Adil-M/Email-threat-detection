from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.core.errors import SentinelError
from app.models.case import Case
from app.models.received_hop import ReceivedHop
from app.schemas.common import APIResponse

router = APIRouter()

@router.get("/cases/{case_id}/observed-infrastructure")
def observed_infrastructure(case_id: str, db: Session = Depends(get_db)):
    case = db.query(Case).filter(Case.id == case_id).first()
    if not case: raise SentinelError("Case not found", status_code=404)
    hops = db.query(ReceivedHop).filter(ReceivedHop.case_id == case.id, ReceivedHop.source_ip.is_not(None)).all()
    return APIResponse(data=[{"ip": hop.source_ip, "label": "Observed infrastructure", "geolocation_status": "unavailable", "confidence": 0.0, "limitation": "No geolocation provider configured; IP does not establish attacker identity."} for hop in hops])
