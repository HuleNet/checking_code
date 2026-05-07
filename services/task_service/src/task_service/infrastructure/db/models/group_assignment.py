from uuid import UUID
from datetime import datetime

from sqlalchemy import DateTime, Enum, Index
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, ARRAY

from task_service.domain.value_objects import Language, GroupAssignmentStatus
from task_service.infrastructure.db.models.base_model import BaseModel


class GroupAssignmentORM(BaseModel):
    __tablename__ = "group_assignments"

    __table_args__ = (
        Index(
            "idx_group_assignment_finalize",
            "deadline",
            "is_finalized",
        ),
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True)
    group_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    assignment_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    allowed_languages: Mapped[list[Language]] = mapped_column(
        ARRAY(Enum(Language, native_enum=False)),
        nullable=False,
    )
    deadline: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    status: Mapped[GroupAssignmentStatus] = mapped_column(
        Enum(GroupAssignmentStatus, native_enum=False), nullable=False
    )
    finalized_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
