from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from uuid import UUID, uuid4
from typing import Any, ClassVar


@dataclass(slots=True, kw_only=True)
class IntegrationEvent:
    event_id: UUID = field(default_factory=uuid4)
    occurred_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    topic: ClassVar[str]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True, kw_only=True)
class SubmissionCreatedEvent(IntegrationEvent):
    topic = "submission.created"
    submission_id: UUID
    assignment_id: UUID
    code: str
    language: str


@dataclass(slots=True, kw_only=True)
class EvaluationCompletedEvent(IntegrationEvent):
    topic = "evaluation.completed"
    submission_id: UUID
    evaluation_id: UUID
    tests_total: int
    tests_passed: int
    status: str
