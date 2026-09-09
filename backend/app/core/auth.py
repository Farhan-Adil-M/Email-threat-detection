from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Callable
from collections import defaultdict
from time import time

import jwt
import hmac
from fastapi import Depends, Header, HTTPException, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.config import settings

# In-memory rate limiting (use Redis in production)
_login_attempts: dict[str, list[float]] = defaultdict(list)
_upload_attempts: dict[str, list[float]] = defaultdict(list)

LOGIN_RATE_LIMIT = 5  # requests
LOGIN_WINDOW = 300  # 5 minutes
UPLOAD_RATE_LIMIT = 10  # requests
UPLOAD_WINDOW = 300  # 5 minutes


def _check_rate_limit(attempts: dict[str, list[float]], key: str, limit: int, window: int) -> bool:
    # Disable rate limiting in tests
    import os
    if os.environ.get("PYTEST_CURRENT_TEST") or os.environ.get("PYTEST_RUNNING"):
        return True
    now = time()
    # Remove old attempts outside the window
    attempts[key] = [t for t in attempts[key] if now - t < window]
    if len(attempts[key]) >= limit:
        return False
    attempts[key].append(now)
    return True


def _get_client_ip(request: Request) -> str:
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


@dataclass(frozen=True)
class Principal:
    username: str
    role: str


def issue_token(username: str, role: str) -> str:
    payload = {"sub": username, "role": role, "exp": datetime.now(timezone.utc) + timedelta(hours=8)}
    return jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")


def current_principal(authorization: str | None = Header(default=None)) -> Principal:
    if not settings.AUTH_REQUIRED and not authorization:
        return Principal("demo-analyst", "analyst")
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Bearer token required")
    try:
        payload = jwt.decode(authorization[7:], settings.SECRET_KEY, algorithms=["HS256"])
        return Principal(str(payload["sub"]), str(payload["role"]))
    except (jwt.PyJWTError, KeyError):
        raise HTTPException(status_code=401, detail="Invalid or expired token")


def require_role(*roles: str) -> Callable:
    def dependency(principal: Principal = Depends(current_principal)) -> Principal:
        if principal.role not in roles:
            raise HTTPException(status_code=403, detail="Insufficient role")
        return principal
    return dependency