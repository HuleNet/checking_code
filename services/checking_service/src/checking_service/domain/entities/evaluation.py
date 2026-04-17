from dataclasses import dataclass, field
from uuid import UUID
from datetime import datetime, timezone

from checking_service.domain.enums import ExecutionStatus, EvaluationStatus
from checking_service.domain.entities import ExecutionCase
from checking_service.domain.errors import InvariantViolationError


@dataclass
class Evaluation:
    id: UUID
    submission_id: UUID
    total_tests_count: int
    status: EvaluationStatus = EvaluationStatus.PENDING
    passed_tests: int = 0
    failed_tests: int = 0
    error_tests: int = 0
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self) -> None:
        self._check_invariants()

    def _check_invariants(self) -> None:
        if self.total_tests_count <= 0:
            raise InvariantViolationError(
                message="Total tests count must be greater than zero",
                details={
                    "total_tests_count": self.total_tests_count,
                },
            )

    def start(self) -> None:
        if self.status == EvaluationStatus.PENDING:
            self.status = EvaluationStatus.RUNNING

    def recalculate(self, cases: list[ExecutionCase]) -> None:
        if self.status in EvaluationStatus.get_finish_statuses():
            return

        self.passed_tests = sum(
            1 for case in cases if case.status == ExecutionStatus.PASSED
        )
        self.failed_tests = sum(
            1 for case in cases if case.status == ExecutionStatus.WRONG_ANSWER
        )
        self.error_tests = sum(
            1 for case in cases if case.status in ExecutionStatus.get_error_statuses()
        )

        if len(cases) < self.total_tests_count:
            self.status = EvaluationStatus.RUNNING
            return

        if self.error_tests > 0:
            self.status = EvaluationStatus.ERROR
        elif self.failed_tests > 0:
            self.status = EvaluationStatus.FAILED
        else:
            self.status = EvaluationStatus.PASSED
