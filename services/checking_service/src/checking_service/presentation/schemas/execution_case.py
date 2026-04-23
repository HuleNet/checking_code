from uuid import UUID

from checking_service.presentation.schemas import BaseSchema


class ExecutionCaseResponse(BaseSchema):
    id: UUID
    evaluation_id: UUID
    input_data: str
    expected_output: str
    check_type: str
    status: str | None
    stdout: str | None
    stderr: str | None
    execution_time_ms: int | None
