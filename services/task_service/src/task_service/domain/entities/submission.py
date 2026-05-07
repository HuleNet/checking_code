from dataclasses import dataclass, field
from uuid import UUID
from datetime import datetime, timezone

from task_service.domain.value_objects import SubmissionStatus, Language, CodeHash
from task_service.domain.events import (
    DomainEvent,
    SubmissionCreatedEvent,
    SubmissionProcessingStartedEvent,
    SubmissionCompletedEvent,
    SubmissionFailedEvent,
)
from task_service.domain.errors import (
    InvariantViolationError,
    BusinessRuleViolationError,
)


@dataclass
class Submission:
    id: UUID
    student_id: UUID
    group_assignment_id: UUID
    language: Language
    code: str
    code_hash: CodeHash
    attempt_number: int
    status: SubmissionStatus = SubmissionStatus.PENDING
    tests_total: int | None = None
    tests_passed: int | None = None
    checked_at: datetime | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    _events: list[DomainEvent] = field(default_factory=list, init=False, repr=False)

    @classmethod
    def create(
        cls,
        id: UUID,
        student_id: UUID,
        group_assignment_id: UUID,
        language: Language,
        code: str,
        code_hash: CodeHash,
        attempt_number: int,
    ) -> "Submission":
        submission = cls(
            id=id,
            student_id=student_id,
            group_assignment_id=group_assignment_id,
            language=language,
            code=code,
            code_hash=code_hash,
            attempt_number=attempt_number,
        )
        submission._add_event(
            SubmissionCreatedEvent(
                submission_id=submission.id,
                student_id=submission.student_id,
                group_assignment_id=submission.group_assignment_id,
                code=submission.code,
                language=submission.language,
            )
        )
        return submission

    def __post_init__(self) -> None:
        self._check_invariants()

    def pull_events(self) -> list[DomainEvent]:
        events = self._events[:]
        self._events.clear()
        return events

    def start_processing(self) -> None:
        if self.status != SubmissionStatus.PENDING:
            raise BusinessRuleViolationError(
                message="Submission status must be PENDING for starting",
                details={
                    "entity": "submission",
                    "id": self.id,
                    "status": self.status.value,
                },
            )

        self.status = SubmissionStatus.IN_PROGRESS
        self._add_event(
            event=SubmissionProcessingStartedEvent(
                submission_id=self.id,
            )
        )

    def apply_result(self, tests_passed: int, tests_total: int) -> None:
        if self.status != SubmissionStatus.IN_PROGRESS:
            raise BusinessRuleViolationError(
                message="Submission status must be IN_PROGRESS for applying result",
                details={
                    "entity": "submission",
                    "id": self.id,
                    "status": self.status.value,
                },
            )

        if tests_passed < 0 or tests_total < 0:
            raise BusinessRuleViolationError(
                message="Total tests and tests passed count must be positive numbers",
                details={
                    "entity": "submission",
                    "id": self.id,
                    "tests_total": tests_total,
                    "tests_passed": tests_passed,
                },
            )

        if tests_passed > tests_total:
            raise BusinessRuleViolationError(
                message="Total tests must be greater or equal than tests passed count",
                details={
                    "entity": "submission",
                    "id": self.id,
                    "tests_total": tests_total,
                    "tests_passed": tests_passed,
                },
            )

        self.tests_total = tests_total
        self.tests_passed = tests_passed
        self.status = SubmissionStatus.COMPLETED
        self.checked_at = datetime.now(timezone.utc)
        self._add_event(
            event=SubmissionCompletedEvent(
                submission_id=self.id,
                tests_total=self.tests_total,
                tests_passed=self.tests_passed,
            )
        )

    def fail(self) -> None:
        if self.status not in (SubmissionStatus.PENDING, SubmissionStatus.IN_PROGRESS):
            raise BusinessRuleViolationError(
                message="Submission status must be IN_PROGRESS for marking failed",
                details={
                    "entity": "submission",
                    "id": self.id,
                    "status": self.status.value,
                },
            )

        self.status = SubmissionStatus.FAILED
        self._add_event(
            SubmissionFailedEvent(
                submission_id=self.id,
            )
        )

    def _add_event(self, event: DomainEvent) -> None:
        self._events.append(event)

    def _check_invariants(self) -> None:
        if not self.code.strip():
            raise InvariantViolationError(
                message="Code must not be empty",
                details={
                    "entity": "submission",
                    "code": self.code,
                },
            )

        if self.attempt_number < 1:
            raise InvariantViolationError(
                message="Attempt number must be greater or equal than 1",
                details={
                    "entity": "submission",
                    "attempt_number": self.attempt_number,
                },
            )
