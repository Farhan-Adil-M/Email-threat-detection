from datetime import datetime
from typing import Any, Generic, TypeVar
from uuid import UUID

from pydantic import BaseModel, ConfigDict

T = TypeVar("T")


class APIResponse(BaseModel, Generic[T]):
    model_config = ConfigDict(from_attributes=True)

    success: bool = True
    data: T | None = None
    error: dict[str, Any] | None = None
    meta: dict[str, Any] = {}


class HealthResponse(BaseModel):
    status: str
    version: str
    database: str
    redis: str
    timestamp: datetime


class CaseCreate(BaseModel):
    title: str
    tags: str | None = None


class CaseRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title: str
    status: str
    severity: str | None
    tags: str | None
    created_by: str | None
    created_at: datetime
    updated_at: datetime


class EvidenceRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    case_id: UUID
    type: str
    sha256: str
    storage_reference: str
    original_filename: str | None
    content_type: str | None
    size: int
    sensitivity: str
    created_at: datetime


class UploadResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    case_id: UUID
    evidence_id: UUID
    sha256: str
    filename: str | None
    size: int
    status: str
    message: str


class AuditEventRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    case_id: UUID
    actor: str
    action: str
    timestamp: datetime
    evidence_refs: str | None
    previous_hash: str | None
    event_hash: str
    canonical_payload: str
    metadata_json: str | None


class LedgerVerifyResponse(BaseModel):
    valid: bool
    event_count: int
    events: list[AuditEventRead]
