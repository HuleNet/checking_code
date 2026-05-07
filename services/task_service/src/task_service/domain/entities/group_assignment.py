from dataclasses import dataclass
from uuid import UUID
from datetime import datetime, timezone

from task_service.domain.value_objects import Language, GroupAssignmentStatus
from task_service.domain.errors import BusinessRuleViolationError


@dataclass
class GroupAssignment:
    id: UUID
    group_id: UUID
    assignment_id: UUID
    allowed_languages: set[Language]
    deadline: datetime
    status: GroupAssignmentStatus = GroupAssignmentStatus.ACTIVE
    finalized_at: datetime | None = None

    def start_finalizing(self) -> None:
        if self.status != GroupAssignmentStatus.ACTIVE:
            return

        self.status = GroupAssignmentStatus.FINALIZING

    def finalize(self) -> None:
        if self.status != GroupAssignmentStatus.FINALIZING:
            return

        self.status = GroupAssignmentStatus.FINALIZED
        self.finalized_at = datetime.now(timezone.utc)

    def reset_finalization(self) -> None:
        self.status = GroupAssignmentStatus.ACTIVE

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
