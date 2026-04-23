from uuid import UUID

from checking_service.application.dto.submission import PreviewSubmissionDTO
from checking_service.presentation.schemas import BaseSchema, ExecutionCaseResponse


class PreviewRunRequest(BaseSchema):
    assignment_id: UUID
    language: str
    code: str

    def to_dto(self) -> PreviewSubmissionDTO:
        return PreviewSubmissionDTO(
            assignment_id=self.assignment_id,
            language=self.language,
            code=self.code,
        )


class PreviewRunResponse(BaseSchema):
    total_tests_count: int
    passed_tests_count: int
    status: str
    summary_execution_case: ExecutionCaseResponse | None
