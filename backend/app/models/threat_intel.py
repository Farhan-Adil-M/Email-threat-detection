import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, Float, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class ThreatIntelResult(Base):
    __tablename__ = "threat_intel_results"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    case_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("cases.id"), nullable=False)
    indicator: Mapped[str] = mapped_column(Text, nullable=False)
    indicator_type: Mapped[str] = mapped_column(String(16), nullable=False)
    provider: Mapped[str] = mapped_column(String(64), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    queried_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )
    data_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")
    confidence: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    source_reference: Mapped[str | None] = mapped_column(Text, nullable=True)
    raw_available: Mapped[bool] = mapped_column(default=False, nullable=False)
