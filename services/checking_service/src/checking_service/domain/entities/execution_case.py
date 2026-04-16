from dataclasses import dataclass
from uuid import UUID

from checking_service.domain.enums import ExecutionStatus
from checking_service.domain.errors import InvariantViolationError


@dataclass(frozen=True)
class ExecutionCase:
    id: UUID
    evaluation_id: UUID
    input_case_id: UUID
    status: ExecutionStatus
    stdout: str
    stderr: str
    execution_time_ms: int

    def __post_init__(self) -> None:
        self._check_invariants()

    def _check_invariants(self) -> None:
        if self.execution_time_ms < 0:
            raise InvariantViolationError(
                message="Execution time must be greater or equal zero",
                details={
                    "execution_time_ms": self.execution_time_ms,
                },
            )
