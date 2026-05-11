from dataclasses import dataclass, field
from uuid import UUID
from datetime import datetime, timezone

from checking_service.domain.value_objects import EvaluationStatus, EvaluationResult
from checking_service.domain.errors import (
    InvariantViolationError,
    BusinessRuleViolationError,
)


@dataclass
class Evaluation:
    id: UUID
    submission_id: UUID
    tests_total: int
    tests_passed: int = 0
    status: EvaluationStatus | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self) -> None:
        self._check_invariants()

    def apply_results(self, evaluation_result: EvaluationResult) -> None:
        if self.status is not None:
            raise BusinessRuleViolationError(
                message="Evaluation can be completed only when status is None",
                details={
                    "entity": "evaluation",
                    "id": self.id,
                    "status": self.status.value,
                },
            )

        if self.tests_total < evaluation_result.tests_passed:
            raise BusinessRuleViolationError(
                message="Passed tests count greater than total tests count",
                details={
                    "entity": "evaluation",
                    "id": self.id,
                    "tests_total": self.tests_total,
                    "tests_passed": evaluation_result.tests_passed,
                },
            )

        self.status = evaluation_result.status
        self.tests_passed = evaluation_result.tests_passed

    def _check_invariants(self) -> None:
        if self.tests_total <= 0:
            raise InvariantViolationError(
                message="Total tests count must be greater than zero",
                details={
                    "entity": "evaluation",
                    "tests_total": self.tests_total,
                },
            )
