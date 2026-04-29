from dataclasses import dataclass, field
from uuid import UUID
from datetime import datetime, timezone

from task_service.domain.enums import SubmissionStatus, Language
from task_service.domain.value_objects import CodeHash
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
    tests_total: int | None
    tests_passed: int | None
    status: SubmissionStatus = SubmissionStatus.PENDING
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    checked_at: datetime | None = None

    def __post_init__(self) -> None:
        self._check_invariants()

    def start_processing(self) -> None:
        if self.status != SubmissionStatus.PENDING:
            raise BusinessRuleViolationError(
                message="Submission status must be PENDING for starting",
                details={
                    "entity": "submission",
                    "id": self.id,
                    "status": self.status,
                },
            )

        self.status = SubmissionStatus.IN_PROGRESS

    def apply_result(self, tests_passed: int, tests_total: int) -> None:
        if self.status != SubmissionStatus.IN_PROGRESS:
            raise BusinessRuleViolationError(
                message="Submission status must be IN_PROGRESS for applying result",
                details={
                    "entity": "submission",
                    "id": self.id,
                    "status": self.status,
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

    def fail(self) -> None:
        if self.status not in (SubmissionStatus.PENDING, SubmissionStatus.IN_PROGRESS):
            raise BusinessRuleViolationError(
                message="Submission status must be IN_PROGRESS for marking failed",
                details={
                    "entity": "submission",
                    "id": self.id,
                    "status": self.status,
                },
            )

        self.status = SubmissionStatus.FAILED

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
