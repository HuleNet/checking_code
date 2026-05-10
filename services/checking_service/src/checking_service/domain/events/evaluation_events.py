from dataclasses import dataclass
from uuid import UUID

from checking_service.domain.value_objects import Language
from checking_service.domain.events import DomainEvent


@dataclass(frozen=True)
class EvaluationStartedEvent(DomainEvent):
    evaluation_id: UUID
    code: str
    language: Language


@dataclass(frozen=True)
class EvaluationCompletedEvent(DomainEvent):
    evaluation_id: UUID


@dataclass(frozen=True)
class EvaluationFailedEvent(DomainEvent):
    evaluation_id: UUID
