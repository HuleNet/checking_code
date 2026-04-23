from uuid import UUID
from datetime import datetime

from checking_service.application.dto.submission import SubmissionDTO
from checking_service.presentation.schemas import BaseSchema


class StartEvaluationRequest(BaseSchema):
    submission_id: UUID
    assignment_id: UUID
    language: str
    code: str

    def to_dto(self) -> SubmissionDTO:
        return SubmissionDTO(
            id=self.submission_id,
            assignment_id=self.assignment_id,
            language=self.language,
            code=self.code,
        )


class EvaluationResponse(BaseSchema):
    id: UUID
    submission_id: UUID
    total_tests_count: int
    passed_tests_count: int
    status: str
    created_at: datetime
    started_at: datetime | None
