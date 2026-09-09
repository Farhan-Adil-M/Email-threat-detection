from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Callable

import jwt
from fastapi import Depends, Header, HTTPException

from app.config import settings


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
