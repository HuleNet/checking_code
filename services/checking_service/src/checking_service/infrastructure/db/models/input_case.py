from uuid import UUID

from sqlalchemy import UUID as DB_UUID, Enum, String
from sqlalchemy.orm import Mapped, mapped_column

from checking_service.domain.enums import CheckType
from checking_service.infrastructure.db.models.base_model import (
    BaseModel,
    MAX_STR_LENGTH,
)


class InputCaseORM(BaseModel):
    __tablename__ = "input_cases"

    id: Mapped[UUID] = mapped_column(DB_UUID(as_uuid=True), primary_key=True)
    assignment_id: Mapped[UUID] = mapped_column(
        DB_UUID(as_uuid=True), nullable=False, index=True
    )
    input_data: Mapped[str] = mapped_column(String(MAX_STR_LENGTH), nullable=False)
    expected_output: Mapped[str] = mapped_column(String(MAX_STR_LENGTH), nullable=False)
    check_type: Mapped[CheckType] = mapped_column(
        Enum(CheckType, native_enum=False), nullable=False
    )
