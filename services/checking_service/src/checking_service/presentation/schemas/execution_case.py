from uuid import UUID

from checking_service.presentation.schemas.base_schema import BaseSchema


class ExecutionCaseResponse(BaseSchema):
    id: UUID
    evaluation_id: UUID
    input_data: str
    expected_output: str
    check_type: str
    stdout: str | None = None
    stderr: str | None = None
    execution_time_ms: int | None = None
    exit_code: int | None = None
