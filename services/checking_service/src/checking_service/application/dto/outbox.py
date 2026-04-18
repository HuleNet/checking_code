from dataclasses import dataclass, field
from uuid import UUID
from datetime import datetime, timezone
from typing import Protocol

from checking_service.domain.enums import BaseEnum, Language


class OutboxStatus(BaseEnum):
    PENDING = "PENDING"
    PUBLISHED = "PUBLISHED"
    FAILED = "FAILED"


class OutboxEventType(BaseEnum):
    RUN_EVALUATION_REQUESTED = "RUN_EVALUATION_REQUESTED"


class OutboxEvent(Protocol): ...


@dataclass(frozen=True)
class RunEvaluationRequested(OutboxEvent):
    evaluation_id: UUID
    submission_id: UUID
    assignment_id: UUID
    language: Language
    code: str


@dataclass(frozen=True)
class OutboxMessage:
    id: UUID
    event_type: OutboxEventType
    payload: OutboxEvent
    status: OutboxStatus = OutboxStatus.PENDING
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    retry_count: int = 0
