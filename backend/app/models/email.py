import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class EmailMessage(Base):
    __tablename__ = "email_messages"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    evidence_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("evidence_objects.id"), nullable=False)
    case_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("cases.id"), nullable=False)

    # Identity headers
    from_address: Mapped[str | None] = mapped_column(String(512), nullable=True)
    from_display_name: Mapped[str | None] = mapped_column(String(512), nullable=True)
    to_addresses: Mapped[str | None] = mapped_column(Text, nullable=True)
    cc_addresses: Mapped[str | None] = mapped_column(Text, nullable=True)
    reply_to: Mapped[str | None] = mapped_column(String(512), nullable=True)
    return_path: Mapped[str | None] = mapped_column(String(512), nullable=True)

    subject: Mapped[str | None] = mapped_column(Text, nullable=True)
    date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    message_id: Mapped[str | None] = mapped_column(String(512), nullable=True, index=True)

    # Body
    body_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    body_html_sanitized: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Raw headers preserved for audit/reproducibility
    raw_headers: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )
