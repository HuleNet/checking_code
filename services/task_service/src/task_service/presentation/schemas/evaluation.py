from uuid import UUID

from task_service.presentation.schemas.base_schema import BaseSchema


class EvaluationResultRequest(BaseSchema):
    id: UUID
    submission_id: UUID
    tests_total: int
    tests_passed: int
