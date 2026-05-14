from uuid import UUID
from typing import TYPE_CHECKING

from sqlalchemy import String, Integer, Enum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID as PG_UUID

from checking_service.domain.value_objects import CheckType
from checking_service.infrastructure.db.models import BaseModel

if TYPE_CHECKING:
    from checking_service.infrastructure.db.models import EvaluationORM


class ExecutionCaseORM(BaseModel):
    __tablename__ = "execution_cases"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True)
    evaluation_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("evaluations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    input_data: Mapped[str] = mapped_column(String(500), nullable=False)
    expected_output: Mapped[str] = mapped_column(String(500), nullable=False)
    check_type: Mapped[CheckType] = mapped_column(
        Enum(CheckType, native_enum=False), nullable=False
    )
    stdout: Mapped[str] = mapped_column(String(500), nullable=False)
    stderr: Mapped[str] = mapped_column(String(500), nullable=False)
    execution_time_ms: Mapped[int] = mapped_column(Integer, nullable=False)
    exit_code: Mapped[int] = mapped_column(Integer, nullable=False)

    evaluation: Mapped["EvaluationORM"] = relationship(back_populates="execution_cases")
