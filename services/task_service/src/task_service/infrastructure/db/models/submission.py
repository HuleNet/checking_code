from uuid import UUID
from datetime import datetime

from sqlalchemy import String, Integer, Enum, DateTime, UniqueConstraint, Index
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID as PG_UUID

from task_service.domain.value_objects import Language, SubmissionStatus
from task_service.infrastructure.db.models.base_model import BaseModel, MAX_CODE_LENGTH


class SubmissionORM(BaseModel):
    __tablename__ = "submissions"

    __table_args__ = (
        UniqueConstraint(
            "student_id",
            "code_hash",
            name="uq_submission_student_code_hash",
        ),
        UniqueConstraint(
            "student_id",
            "group_assignment_id",
            "attempt_number",
            name="uq_submission_attempt",
        ),
        Index(
            "idx_submission_student_assignment_attempt",
            "student_id",
            "group_assignment_id",
            "attempt_number",
        ),
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True)
    student_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    group_assignment_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), nullable=False, index=True
    )
    language: Mapped[Language] = mapped_column(
        Enum(Language, native_enum=False), nullable=False
    )
    code: Mapped[str] = mapped_column(String(MAX_CODE_LENGTH), nullable=False)
    code_hash: Mapped[str] = mapped_column(String(128), nullable=False)
    attempt_number: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[SubmissionStatus] = mapped_column(
        Enum(SubmissionStatus, native_enum=False),
        nullable=False,
        index=True,
    )
    tests_passed: Mapped[int | None] = mapped_column(Integer, nullable=True)
    tests_total: Mapped[int | None] = mapped_column(Integer, nullable=True)
    checked_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
