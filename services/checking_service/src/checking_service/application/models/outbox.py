from dataclasses import dataclass, field
from uuid import UUID
from datetime import datetime, timezone
from typing import Any

from checking_service.domain.enums import Language
from checking_service.application.models.enums import OutboxStatus


@dataclass(frozen=True)
class RunEvaluationRequested:
    evaluation_id: UUID
    submission_id: UUID
    assignment_id: UUID
    language: Language
    code: str


@dataclass(frozen=True)
class OutboxMessage:
    id: UUID
    event_type: str
    payload: dict[str, Any]
    status: OutboxStatus = OutboxStatus.PENDING
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    retry_count: int = 0
