from uuid import UUID
from datetime import datetime

from task_service.application.dto.submission import CreateSubmissionDTO
from task_service.presentation.schemas.base_schema import BaseSchema


class SubmissionResponse(BaseSchema):
    id: UUID
    student_id: UUID
    assignment_id: UUID
    group_assignment_id: UUID
    language: str
    code: str
    code_hash: str
    attempt_number: int
    status: str
    tests_total: int | None
    tests_passed: int | None
    evaluation_status: str | None
    checked_at: datetime | None
    created_at: datetime


class CreateSubmissionRequest(BaseSchema):
    student_id: UUID
    group_assignment_id: UUID
    language: str
    code: str

    def to_dto(self) -> CreateSubmissionDTO:
        return CreateSubmissionDTO(
            student_id=self.student_id,
            group_assignment_id=self.group_assignment_id,
            language=self.language,
            code=self.code,
        )
