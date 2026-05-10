from uuid import UUID
from datetime import datetime

from sqlalchemy import String, DateTime, JSON, Index
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID as PG_UUID

from checking_service.infrastructure.db.models import BaseModel


class OutboxMessageORM(BaseModel):
    __tablename__ = "outbox_messages"

    __table_args__ = (
        Index(
            "idx_outbox_unprocessed",
            "processed_at",
            "occurred_at",
        ),
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True)
    event_type: Mapped[str] = mapped_column(String(255), nullable=False)
    payload: Mapped[dict] = mapped_column(JSON, nullable=False)
    occurred_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    processed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, index=True
    )
