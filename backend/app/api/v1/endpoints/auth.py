from fastapi import APIRouter, Depends, Request, HTTPException
from app.config import settings
from app.core.auth import Principal, current_principal, issue_token, _check_rate_limit, _get_client_ip, _login_attempts
from app.core.errors import SentinelError
from app.schemas.common import APIResponse, LoginRequest, LoginResponse
import hmac

router = APIRouter()


@router.post("/login", response_model=APIResponse[LoginResponse])
def login(request: Request, payload: LoginRequest):
    client_ip = _get_client_ip(request)
    if not _check_rate_limit(_login_attempts, f"login:{client_ip}", 5, 300):
        raise HTTPException(status_code=429, detail="Too many login attempts. Try again later.")

    credentials = {
        "analyst": settings.DEMO_ANALYST_PASSWORD,
        "admin": settings.DEMO_ADMIN_PASSWORD,
    }
    if payload.username not in credentials:
        raise SentinelError("Invalid credentials", status_code=401)
    
    # Constant-time comparison
    expected = credentials[payload.username].encode()
    provided = payload.password.encode()
    if not hmac.compare_digest(expected, provided):
        raise SentinelError("Invalid credentials", status_code=401)
    
    token = issue_token(payload.username, payload.username)
    return APIResponse(data=LoginResponse(access_token=token, role=payload.username))


@router.get("/me", response_model=APIResponse[dict])
def me(principal: Principal = Depends(current_principal)):
    return APIResponse(data={"username": principal.username, "role": principal.role})