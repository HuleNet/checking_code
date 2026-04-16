from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class ExecutionCaseDTO:
    id: UUID
    evaluation_id: UUID
    input_case_id: UUID
    status: str
    stdout: str
    stderr: str
    execution_time_ms: int


@dataclass(frozen=True)
class CreateExecutionCaseDTO:
    evaluation_id: UUID
    input_case_id: UUID
    status: str
    stdout: str
    stderr: str
    executioN_time_ms: int
