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


class EmailMessageRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    evidence_id: UUID
    case_id: UUID
    from_address: str | None
    from_display_name: str | None
    to_addresses: str | None
    cc_addresses: str | None
    reply_to: str | None
    return_path: str | None
    subject: str | None
    date: datetime | None
    message_id: str | None
    body_text: str | None
    body_html_sanitized: str | None
    created_at: datetime


class ReceivedHopRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    email_id: UUID
    hop_index: int
    source_host: str | None
    source_ip: str | None
    destination_host: str | None
    protocol: str | None
    timestamp: datetime | None
    is_private_ip: bool
    is_malformed: bool
    missing_data: bool


class AuthenticationResultRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    email_id: UUID
    mechanism: str
    domain: str | None
    result: str | None
    alignment: str | None
    policy: str | None
    explanation: str | None


class FindingRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    case_id: UUID
    email_id: UUID | None
    rule_id: str
    category: str
    severity: str
    title: str
    description: str
    evidence_refs: str
    score_delta: int
    confidence: float
    status: str
    created_at: datetime


class AnalyzeResponse(BaseModel):
    case_id: UUID
    email_id: UUID
    message_id: str | None
    findings_count: int
    hops_count: int
    auth_count: int
    status: str
    message: str
