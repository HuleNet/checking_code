from typing import Any

from checking_service.domain.events import (
    DomainEvent,
    EvaluationStartedEvent,
    EvaluationCompletedEvent,
    EvaluationFailedEvent,
)
from checking_service.application.errors import ValidationError


class EventMapper:
    @staticmethod
    def serialize_event(event: DomainEvent) -> dict[str, Any]:
        if isinstance(event, EvaluationStartedEvent):
            return {
                "evaluation_id": str(event.evaluation_id),
                "code": event.code,
                "language": event.language.value,
            }

        if isinstance(event, EvaluationCompletedEvent):
            return {
                "evaluation_id": str(event.evaluation_id),
            }

        if isinstance(event, EvaluationFailedEvent):
            return {
                "evaluation_id": str(event.evaluation_id),
            }

        raise ValidationError(
            message="Failed to serialize event",
            details={
                "event": event.__class__.__name__,
            },
        )
