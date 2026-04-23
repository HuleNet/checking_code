from uuid import UUID

from checking_service.application.dto.input_case import (
    CreateInputCaseDTO,
    UpdateInputCaseDTO,
)
from checking_service.presentation.schemas import BaseSchema


class CreateInputCaseRequest(BaseSchema):
    assignment_id: UUID
    input_data: str
    expected_output: str
    check_type: str

    def to_dto(self) -> CreateInputCaseDTO:
        return CreateInputCaseDTO(
            assignment_id=self.assignment_id,
            input_data=self.input_data,
            expected_output=self.expected_output,
            check_type=self.check_type,
        )


class UpdateInputCaseRequest(BaseSchema):
    input_data: str | None = None
    expected_output: str | None = None
    check_type: str | None = None

    def to_dto(self) -> UpdateInputCaseDTO:
        return UpdateInputCaseDTO(
            input_data=self.input_data,
            expected_output=self.expected_output,
            check_type=self.check_type,
        )


class InputCaseResponse(BaseSchema):
    id: UUID
    assignment_id: UUID
    input_data: str
    expected_output: str
    check_type: str
