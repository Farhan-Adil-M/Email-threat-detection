import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Float, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class MLAssessment(Base):
    __tablename__ = "ml_assessments"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    case_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("cases.id"), nullable=False)
    email_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("email_messages.id"), nullable=False)
    model_version: Mapped[str] = mapped_column(String(64), nullable=False)
    phishing_probability: Mapped[float] = mapped_column(Float, nullable=False)
    bec_probability: Mapped[float] = mapped_column(Float, nullable=False)
    impersonation_probability: Mapped[float] = mapped_column(Float, nullable=False)
    important_features_json: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    limitations_json: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )
