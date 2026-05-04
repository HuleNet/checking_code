from dataclasses import dataclass
from uuid import UUID

from task_service.domain.enums import Language
from task_service.domain.events import DomainEvent


@dataclass(frozen=True)
class SubmissionCreatedEvent(DomainEvent):
    submission_id: UUID
    student_id: UUID
    group_assignment_id: UUID
    code: str
    language: Language


@dataclass(frozen=True)
class SubmissionProcessingStartedEvent(DomainEvent):
    submission_id: UUID


@dataclass(frozen=True)
class SubmissionCompletedEvent(DomainEvent):
    submission_id: UUID
    tests_passed: int
    tests_total: int


@dataclass(frozen=True)
class SubmissionFailedEvent(DomainEvent):
    submission_id: UUID
