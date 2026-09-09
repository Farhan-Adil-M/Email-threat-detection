from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.config import settings
from app.core.errors import SentinelError
from app.models.case import Case
from app.models.received_hop import ReceivedHop
from app.schemas.common import APIResponse

router = APIRouter()


def _parse_uuid(case_id: str) -> UUID:
    try:
        return UUID(case_id)
    except ValueError:
        raise SentinelError("Invalid case ID", status_code=400)


@router.get("/cases/{case_id}/observed-infrastructure")
def observed_infrastructure(case_id: str, db: Session = Depends(get_db)):
    case_uuid = _parse_uuid(case_id)
    case = db.query(Case).filter(Case.id == case_uuid).first()
    if not case:
        raise SentinelError("Case not found", status_code=404)

    hops = (
        db.query(ReceivedHop)
        .filter(ReceivedHop.case_id == case.id, ReceivedHop.source_ip.is_not(None))
        .all()
    )

    mode = settings.INTEL_MODE.lower()
    results = []
    for hop in hops:
        ip = hop.source_ip
        entry = {
            "ip": ip,
            "label": "Observed infrastructure",
            "is_private_ip": hop.is_private_ip,
            "source_host": hop.source_host,
            "protocol": hop.protocol,
            "hop_index": hop.hop_index,
        }

        if hop.is_private_ip:
            entry["geolocation_status"] = "not_applicable"
            entry["confidence"] = 0.0
            entry["limitation"] = "Private/reserved IP — no external lookup performed."
            results.append(entry)
            continue

        if mode == "live":
            try:
                from app.services.intelligence.providers_ipinfo import IPInfoProvider
                provider = IPInfoProvider(timeout=getattr(settings, "INTEL_IPINFO_TIMEOUT", 2.0))
                intel = provider.lookup(ip, "ip")
                entry["geolocation_status"] = intel.status
                entry["confidence"] = intel.confidence
                entry["data"] = intel.data
                entry["provider"] = intel.provider
                entry["source_reference"] = intel.source_reference
                if intel.status != "success":
                    entry["limitation"] = intel.data.get("reason", "Lookup failed")
            except Exception as e:
                entry["geolocation_status"] = "error"
                entry["confidence"] = 0.0
                entry["limitation"] = str(e)
        elif mode == "fixture":
            entry["geolocation_status"] = "fixture"
            entry["confidence"] = 0.0
            entry["data"] = {"mode": "deterministic", "note": "No live provider queried."}
            entry["limitation"] = "Deterministic mode — no live geolocation performed."
        else:
            entry["geolocation_status"] = "unavailable"
            entry["confidence"] = 0.0
            entry["limitation"] = "No geolocation provider configured; IP does not establish attacker identity."

        results.append(entry)

    return APIResponse(data=results)
