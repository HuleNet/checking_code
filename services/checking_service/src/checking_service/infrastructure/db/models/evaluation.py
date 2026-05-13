from uuid import UUID
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Integer, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID as PG_UUID

from checking_service.domain.value_objects import EvaluationStatus
from checking_service.infrastructure.db.models import BaseModel

if TYPE_CHECKING:
    from checking_service.infrastructure.db.models import ExecutionCaseORM


class EvaluationORM(BaseModel):
    __tablename__ = "evaluations"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True)
    submission_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), nullable=False, index=True
    )
    tests_total: Mapped[int] = mapped_column(Integer, nullable=False)
    tests_passed: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[EvaluationStatus] = mapped_column(
        Enum(EvaluationStatus, native_enum=False), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )

    execution_cases: Mapped[list["ExecutionCaseORM"]] = relationship(
        back_populates="evaluation", cascade="all, delete-orphan"
    )
