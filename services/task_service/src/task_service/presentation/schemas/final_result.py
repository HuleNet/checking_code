from uuid import UUID
from datetime import datetime

from task_service.presentation.schemas.base_schema import BaseSchema


class FinalResultResponse(BaseSchema):
    id: UUID
    group_assignment_id: UUID
    student_id: UUID
    submission_id: UUID
    score: int
    attempt_number: int
    tests_total: int
    tests_passed: int
    evaluation_status: str
    finalized_at: datetime
