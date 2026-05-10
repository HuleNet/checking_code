from uuid import UUID

from checking_service.application.dto.test_case import (
    CreateTestCaseDTO,
    UpdateTestCaseDTO,
)
from checking_service.presentation.schemas.base_schema import BaseSchema


class CreateTestCaseRequest(BaseSchema):
    assignment_id: UUID
    input_data: str
    expected_output: str
    check_type: str

    def to_dto(self) -> CreateTestCaseDTO:
        return CreateTestCaseDTO(
            assignment_id=self.assignment_id,
            input_data=self.input_data,
            expected_output=self.expected_output,
            check_type=self.check_type,
        )


class UpdateTestCaseRequest(BaseSchema):
    input_data: str | None = None
    expected_output: str | None = None
    check_type: str | None = None

    def to_dto(self) -> UpdateTestCaseDTO:
        return UpdateTestCaseDTO(
            input_data=self.input_data,
            expected_output=self.expected_output,
            check_type=self.check_type,
        )


class TestCaseResponse(BaseSchema):
    id: UUID
    assignment_id: UUID
    input_data: str
    expected_output: str
    check_type: str
