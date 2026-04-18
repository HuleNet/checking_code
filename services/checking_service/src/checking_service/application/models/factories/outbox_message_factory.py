from uuid import UUID

from checking_service.domain.entities import Submission
from checking_service.application.models.outbox import (
    OutboxMessage,
    RunEvaluationRequested,
)


class OutboxMessageFactory:
    @staticmethod
    def create_run_evaluation_event(
        evaluation_id: UUID,
        submission: Submission,
    ) -> RunEvaluationRequested:
        return RunEvaluationRequested(
            evaluation_id=evaluation_id,
            submission_id=submission.id,
            assignment_id=submission.assignment_id,
            language=submission.language,
            code=submission.code,
        )

    @staticmethod
    def create_run_evaluation_message(
        id: UUID,
        event: RunEvaluationRequested,
    ) -> OutboxMessage:
        return OutboxMessage(
            id=id,
            event_type="RUN_EVALUATION_REQUESTED",
            payload={
                "evaluation_id": str(event.evaluation_id),
                "submission_id": str(event.submission_id),
                "assignment_id": str(event.assignment_id),
                "language": event.language.value,
                "code": event.code,
            },
        )
