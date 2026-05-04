from typing import Any

from task_service.domain.events import (
    DomainEvent,
    SubmissionCreatedEvent,
    SubmissionProcessingStartedEvent,
    SubmissionCompletedEvent,
    SubmissionFailedEvent,
)
from task_service.application.errors import ValidationError


class EventMapper:
    @staticmethod
    def serialize_event(event: DomainEvent) -> dict[str, Any]:
        if isinstance(event, SubmissionCreatedEvent):
            return {
                "submission_id": str(event.submission_id),
                "student_id": str(event.student_id),
                "group_assignment_id": str(event.group_assignment_id),
                "code": event.code,
                "language": event.language.value,
            }

        if isinstance(event, SubmissionProcessingStartedEvent):
            return {
                "submission_id": str(event.submission_id),
            }

        if isinstance(event, SubmissionCompletedEvent):
            return {
                "submission_id": str(event.submission_id),
                "tests_passed": event.tests_passed,
                "tests_total": event.tests_total,
            }

        if isinstance(event, SubmissionFailedEvent):
            return {
                "submission_id": str(event.submission_id),
            }

        raise ValidationError(
            message="Failed to serialize event",
            details={
                "event": event.__class__.__name__,
            },
        )
