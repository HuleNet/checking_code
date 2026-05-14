from uuid import UUID
from datetime import datetime

from sqlalchemy import Integer, DateTime, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID as PG_UUID

from task_service.infrastructure.db.models import BaseModel


class FinalResultORM(BaseModel):
    __tablename__ = "final_results"

    __table_args__ = (
        UniqueConstraint(
            "group_assignment_id",
            "student_id",
            name="uq_final_result_group_assignment_student",
        ),
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True)
    group_assignment_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), nullable=False, index=True
    )
    student_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), nullable=False, index=True
    )
    submission_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), nullable=False, index=True
    )
    score: Mapped[int] = mapped_column(Integer, nullable=False)
    attempt_number: Mapped[int] = mapped_column(Integer, nullable=False)
    tests_total: Mapped[int] = mapped_column(Integer, nullable=False)
    tests_passed: Mapped[int] = mapped_column(Integer, nullable=False)
    evaluation_status: Mapped[str] = mapped_column(String(50), nullable=False)
    finalized_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
