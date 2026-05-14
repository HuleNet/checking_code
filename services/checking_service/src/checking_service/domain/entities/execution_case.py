from dataclasses import dataclass
from uuid import UUID

from checking_service.domain.value_objects import CheckType
from checking_service.domain.errors import (
    InvariantViolationError,
    BusinessRuleViolationError,
)


@dataclass
class ExecutionCase:
    id: UUID
    evaluation_id: UUID

    # test case snapshot
    input_data: str
    expected_output: str
    check_type: CheckType

    # execution result
    stdout: str | None = None
    stderr: str | None = None
    execution_time_ms: int | None = None
    exit_code: int | None = None

    def __post_init__(self) -> None:
        self._check_invariants()

    def apply_result(
        self,
        stdout: str,
        stderr: str,
        execution_time_ms: int,
        exit_code: int,
    ) -> None:
        if execution_time_ms < 0:
            raise BusinessRuleViolationError(
                message="Execution time must be greater or equal zero",
                details={
                    "entity": "execution_case",
                    "id": self.id,
                    "execution_time_ms": execution_time_ms,
                },
            )

        self.stdout = stdout
        self.stderr = stderr
        self.execution_time_ms = execution_time_ms
        self.exit_code = exit_code

    def _check_invariants(self) -> None:
        if not self.input_data and not self.expected_output:
            raise InvariantViolationError(
                message="Input data or expected output must not be empty",
                details={
                    "entity": "execution_case",
                    "input_data": self.input_data,
                    "expected_output": self.expected_output,
                },
            )
