from uuid import UUID

from sqlalchemy import Enum, String
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID as PG_UUID

from checking_service.domain.value_objects import CheckType
from checking_service.infrastructure.db.models.base_model import (
    BaseModel,
    MAX_STR_LENGTH,
)


class TestCaseORM(BaseModel):
    __tablename__ = "test_cases"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True)
    assignment_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), nullable=False, index=True
    )
    input_data: Mapped[str] = mapped_column(String(MAX_STR_LENGTH), nullable=False)
    expected_output: Mapped[str] = mapped_column(String(MAX_STR_LENGTH), nullable=False)
    check_type: Mapped[CheckType] = mapped_column(
        Enum(CheckType, native_enum=False), nullable=False
    )
