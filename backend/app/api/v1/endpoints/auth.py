from fastapi import APIRouter, Depends
from app.config import settings
from app.core.auth import Principal, current_principal, issue_token
from app.schemas.common import APIResponse, LoginRequest, LoginResponse

router = APIRouter()

@router.post("/login", response_model=APIResponse[LoginResponse])
def login(payload: LoginRequest):
    credentials = {
        "analyst": settings.DEMO_ANALYST_PASSWORD,
        "admin": settings.DEMO_ADMIN_PASSWORD,
    }
    if payload.username not in credentials or payload.password != credentials[payload.username]:
        from app.core.errors import SentinelError
        raise SentinelError("Invalid credentials", status_code=401)
    token = issue_token(payload.username, payload.username)
    return APIResponse(data=LoginResponse(access_token=token, role=payload.username))

@router.get("/me", response_model=APIResponse[dict])
def me(principal: Principal = Depends(current_principal)):
    return APIResponse(data={"username": principal.username, "role": principal.role})
