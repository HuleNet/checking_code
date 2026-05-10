from uuid import UUID
from datetime import datetime

from checking_service.application.dto.submission import (
    SubmissionDTO,
    PreviewSubmissionDTO,
)
from checking_service.presentation.schemas.base_schema import BaseSchema


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


class PreviewStartEvaluationRequest(BaseSchema):
    assignment_id: UUID
    language: str
    code: str

    def to_dto(self) -> PreviewSubmissionDTO:
        return PreviewSubmissionDTO(
            assignment_id=self.assignment_id,
            language=self.language,
            code=self.code,
        )


class EvaluationResponse(BaseSchema):
    id: UUID
    submission_id: UUID
    tests_total: int
    tests_passed: int
    status: str
    created_at: datetime
    started_at: datetime | None


class PreviewEvaluationResponse(BaseSchema):
    tests_total: int
    tests_passed: int
    status: str
