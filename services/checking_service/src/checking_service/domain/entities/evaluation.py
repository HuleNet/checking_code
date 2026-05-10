from dataclasses import dataclass, field
from uuid import UUID
from datetime import datetime, timezone

from checking_service.domain.value_objects import EvaluationStatus, EvaluationResult
from checking_service.domain.events import (
    DomainEvent,
    EvaluationCompletedEvent,
    EvaluationFailedEvent,
)
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
    status: EvaluationStatus = EvaluationStatus.PENDING
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    started_at: datetime | None = None

    _events: list[DomainEvent] = field(default_factory=list, init=False, repr=False)

    @classmethod
    def create(
        cls,
        id: UUID,
        submission_id: UUID,
        tests_total: int,
    ) -> "Evaluation":
        evaluation = cls(
            id=id,
            submission_id=submission_id,
            tests_total=tests_total,
        )
        return evaluation

    def __post_init__(self) -> None:
        self._check_invariants()

    def apply_results(self, evaluation_result: EvaluationResult) -> None:
        if self.status != EvaluationStatus.RUNNING:
            raise BusinessRuleViolationError(
                message="Evaluation can be recalculated only from RUNNING",
                details={
                    "entity": "evaluation",
                    "id": self.id,
                    "status": self.status.value,
                },
            )

        if evaluation_result.status not in EvaluationStatus.get_finish_statuses():
            raise BusinessRuleViolationError(
                message="Evaluation result have unfinished status",
                details={
                    "entity": "evaluation",
                    "id": self.id,
                    "status": evaluation_result.status.value,
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
        self._add_event(event=EvaluationCompletedEvent(evaluation_id=self.id))

    def fail(self) -> None:
        self.status = EvaluationStatus.ERROR
        self._add_event(event=EvaluationFailedEvent(evaluation_id=self.id))

    def pull_events(self) -> list[DomainEvent]:
        events = self._events[:]
        self._events.clear()
        return events

    def _add_event(self, event: DomainEvent) -> None:
        self._events.append(event)

    def _check_invariants(self) -> None:
        if self.tests_total <= 0:
            raise InvariantViolationError(
                message="Total tests count must be greater than zero",
                details={
                    "entity": "evaluation",
                    "tests_total": self.tests_total,
                },
            )
