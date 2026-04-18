from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class ExecutionCaseDTO:
    id: UUID
    evaluation_id: UUID
    input_data: str
    expected_output: str
    check_type: str
    status: str | None
    stdout: str | None
    stderr: str | None
    execution_time_ms: int | None


@dataclass(frozen=True)
class UpdateExecutionCaseDTO:
    status: str
    stdout: str
    stderr: str
    execution_time_ms: int
