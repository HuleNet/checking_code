from dataclasses import dataclass, field
from uuid import UUID
from datetime import datetime, timezone

from checking_service.domain.enums import ExecutionStatus, EvaluationStatus
from checking_service.domain.entities import ExecutionCase
from checking_service.domain.errors import (
    InvariantViolationError,
    BusinessRuleViolationError,
)


@dataclass
class Evaluation:
    id: UUID
    submission_id: UUID
    total_tests_count: int
    passed_tests_count: int = 0
    status: EvaluationStatus = EvaluationStatus.PENDING
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self) -> None:
        self._check_invariants()

    def start(self) -> None:
        if self.status != EvaluationStatus.PENDING:
            raise BusinessRuleViolationError(
                message="Evaluation can be started only from PENDING",
                details={
                    "status": self.status.value,
                },
            )

        self.status = EvaluationStatus.RUNNING

    def fail(self) -> None:
        self.status = EvaluationStatus.ERROR

    def recalculate(self, execution_cases: list[ExecutionCase]) -> None:
        if self.status != EvaluationStatus.RUNNING:
            raise BusinessRuleViolationError(
                message="Evaluation can be recalculated only from RUNNING",
                details={
                    "status": self.status.value,
                },
            )
        if len(execution_cases) != self.total_tests_count:
            raise BusinessRuleViolationError(
                message="InputCase/ExecutionCase count mismatch",
                details={
                    "total_tests_count": self.total_tests_count,
                    "execution_results_count": len(execution_cases),
                },
            )

        self.passed_tests_count = sum(
            1
            for execution_case in execution_cases
            if execution_case.status == ExecutionStatus.PASSED
        )

        if self.passed_tests_count == self.total_tests_count:
            self.status = EvaluationStatus.PASSED
        else:
            self.status = EvaluationStatus.FAILED

    def _check_invariants(self) -> None:
        if self.total_tests_count <= 0:
            raise InvariantViolationError(
                message="Total tests count must be greater than zero",
                details={
                    "total_tests_count": self.total_tests_count,
                },
            )
