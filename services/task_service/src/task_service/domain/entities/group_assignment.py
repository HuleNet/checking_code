from dataclasses import dataclass, field
from uuid import UUID
from datetime import datetime, timezone

from task_service.domain.enums import Language
from task_service.domain.errors import (
    InvariantViolationError,
    BusinessRuleViolationError,
)


@dataclass(frozen=True)
class GroupAssignment:
    id: UUID
    group_id: UUID
    assignment_id: UUID
    allowed_languages: set[Language]
    deadline: datetime
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self) -> None:
        self._check_invariants()

    def ensure_not_expired(self, now: datetime) -> None:
        if now > self.deadline:
            raise BusinessRuleViolationError(
                message="Deadline expired",
                details={
                    "entity": "group_assignment",
                    "id": self.id,
                    "submission_timestamp": now,
                    "deadline": self.deadline,
                },
            )

    def ensure_language_allowed(self, language: Language) -> None:
        if language not in self.allowed_languages:
            raise BusinessRuleViolationError(
                message="Language not allowed",
                details={
                    "entity": "group_assignment",
                    "id": self.id,
                    "language": language.value,
                    "allowed_languages": list(
                        map(lambda language: language.value, self.allowed_languages)
                    ),
                },
            )

    def _check_invariants(self) -> None:
        if self.deadline <= self.created_at:
            raise InvariantViolationError(
                message="Deadline must be later than creation timestamp",
                details={
                    "entity": "group_assignment",
                    "deadline": self.deadline,
                    "created_at": self.created_at,
                },
            )
