from dataclasses import dataclass
from uuid import UUID

from checking_service.domain.enums import ExecutionStatus, CheckType
from checking_service.domain.errors import InvariantViolationError


@dataclass
class ExecutionCase:
    id: UUID

    # input case snapshot
    evaluation_id: UUID
    input_data: str
    expected_output: str
    check_type: CheckType

    # execution result
    status: ExecutionStatus | None = None
    stdout: str | None = None
    stderr: str | None = None
    execution_time_ms: int | None = None

    def __post_init__(self) -> None:
        self._check_base_invariants()

    def apply_result(
        self, status: ExecutionStatus, stdout: str, stderr: str, execution_time_ms: int
    ) -> None:
        if self.status is not None:
            return

        self.status = status
        self.stdout = stdout
        self.stderr = stderr
        self.execution_time_ms = execution_time_ms
        self._check_result_invariants()

    def _check_base_invariants(self) -> None:
        if not self.input_data and not self.expected_output:
            raise InvariantViolationError(
                message="Input data or expected output must not be empty",
                details={
                    "input_data": self.input_data,
                    "expected_output": self.expected_output,
                },
            )

    def _check_result_invariants(self) -> None:
        if self.status is None:
            raise InvariantViolationError(
                message="ExecutionCase must have status after apply results",
                details={
                    "status": self.status,
                },
            )

        if self.stdout is None:
            raise InvariantViolationError(
                message="ExecutionCase must have stdout after apply results",
                details={
                    "status": self.stdout,
                },
            )

        if self.stderr is None:
            raise InvariantViolationError(
                message="ExecutionCase must have stderr after apply results",
                details={
                    "status": self.stderr,
                },
            )

        if self.execution_time_ms is None:
            raise InvariantViolationError(
                message="ExecutionCase must have execution time after apply results",
                details={
                    "execution_time_ms": self.execution_time_ms,
                },
            )

        if self.execution_time_ms < 0:
            raise InvariantViolationError(
                message="Execution time must be greater or equal zero",
                details={
                    "execution_time_ms": self.execution_time_ms,
                },
            )
