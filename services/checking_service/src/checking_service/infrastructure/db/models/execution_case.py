from uuid import UUID
from typing import TYPE_CHECKING

from sqlalchemy import UUID as DB_UUID, String, Integer, Enum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from checking_service.domain.enums import ExecutionStatus, CheckType
from checking_service.infrastructure.db.models.base_model import (
    BaseModel,
    MAX_STR_LENGTH,
)

if TYPE_CHECKING:
    from checking_service.infrastructure.db.models import EvaluationORM


class ExecutionCaseORM(BaseModel):
    __tablename__ = "execution_cases"

    id: Mapped[UUID] = mapped_column(DB_UUID(as_uuid=True), primary_key=True)
    evaluation_id: Mapped[UUID] = mapped_column(
        DB_UUID(as_uuid=True),
        ForeignKey("evaluations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    input_data: Mapped[str] = mapped_column(String(MAX_STR_LENGTH), nullable=False)
    expected_output: Mapped[str] = mapped_column(String(MAX_STR_LENGTH), nullable=False)
    check_type: Mapped[CheckType] = mapped_column(
        Enum(CheckType, native_enum=False), nullable=False
    )
    status: Mapped[ExecutionStatus | None] = mapped_column(
        Enum(ExecutionStatus, native_enum=False), nullable=True
    )
    stdout: Mapped[str | None] = mapped_column(String(MAX_STR_LENGTH), nullable=True)
    stderr: Mapped[str | None] = mapped_column(String(MAX_STR_LENGTH), nullable=True)
    execution_time_ms: Mapped[int | None] = mapped_column(Integer(), nullable=True)

    evaluation: Mapped["EvaluationORM"] = relationship(back_populates="execution_cases")
