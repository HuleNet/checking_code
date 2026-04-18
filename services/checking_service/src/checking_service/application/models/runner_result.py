from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class RunnerResult:
    execution_case_id: UUID
    stdout: str
    stderr: str
    execution_time_ms: int
    exit_code: int
    timeout: bool = False
    memory_exceeded: bool = False
