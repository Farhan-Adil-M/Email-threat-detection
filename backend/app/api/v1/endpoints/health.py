from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from redis import Redis
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.schemas.common import APIResponse, HealthResponse

router = APIRouter()


def get_redis() -> Redis:
    return Redis.from_url(settings.REDIS_URL, decode_responses=True)


@router.get("", response_model=APIResponse[HealthResponse])
def health_check(db: Session = Depends(get_db)):
    redis_status = "unknown"
    db_status = "unknown"

    try:
        r = get_redis()
        r.ping()
        redis_status = "ok"
    except Exception:
        redis_status = "unavailable"

    try:
        db.execute(text("SELECT 1"))
        db_status = "ok"
    except Exception:
        db_status = "unavailable"

    health = HealthResponse(
        status="ok" if db_status == "ok" else "degraded",
        version="0.1.0",
        database=db_status,
        redis=redis_status,
        timestamp=datetime.now(timezone.utc),
    )

    return APIResponse(data=health)
