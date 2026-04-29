from dataclasses import dataclass, field
from uuid import UUID
from datetime import datetime, timezone

from task_service.domain.errors import InvariantViolationError


@dataclass(frozen=True)
class FinalResult:
    id: UUID
    group_assignment_id: UUID
    student_id: UUID
    submission_id: UUID
    score: int
    attempt_number: int
    tests_total: int
    tests_passed: int
    plagiarism_score: float
    plagiarism_flag: bool 
    finalized_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self) -> None:
        self._check_invariants()

    def _check_invariants(self) -> None:
        if self.attempt_number < 1:
            raise InvariantViolationError(
                message="Attempt number must be greater or equal than 1",
                details={
                    "entity": "final_result",
                    "attempt_number": self.attempt_number,
                },
            )
        if not (0 < self.score < 100):
            raise InvariantViolationError(
                message="Score must be in 0 to 100 interval",
                details={
                    "entity": "final_result",
                    "score": self.score,
                },
            )

        if self.tests_passed < 0 or self.tests_total < 0:
            raise InvariantViolationError(
                message="Total tests and tests passed count must be positive numbers",
                details={
                    "entity": "final_result",
                    "tests_total": self.tests_total,
                    "tests_passed": self.tests_passed,
                },
            )

        if self.tests_passed > self.tests_total:
            raise InvariantViolationError(
                message="Total tests must be greater or equal than tests passed count",
                details={
                    "entity": "final_result",
                    "tests_total": self.tests_total,
                    "tests_passed": self.tests_passed,
                },
            )
        
        if not (0 < self.plagiarism_score < 1):
            raise InvariantViolationError(
                message="Plagiarism score must be in 0 to 1 interval",
                details={
                    "entity": "final_result",
                    "plagiarism_score": self.plagiarism_score,
                },
            )
