from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class ExecutionCaseDTO:
    id: UUID
    evaluation_id: UUID
    input_data: str
    expected_output: str
    check_type: str
    stdout: str | None = None
    stderr: str | None = None
    execution_time_ms: int | None = None
    exit_code: int | None = None
    is_timeout: bool | None = None
    is_memory_exceeded: bool | None = None


@dataclass(frozen=True)
class ExecutionCaseResultDTO:
    id: UUID
    stdout: str
    stderr: str
    execution_time_ms: int
    exit_code: int
    is_timeout: bool
    is_memory_exceeded: bool
