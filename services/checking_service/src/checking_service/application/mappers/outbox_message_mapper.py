from uuid import UUID

from checking_service.domain.entities import Submission
from checking_service.application.dto.outbox import (
    OutboxMessage,
    OutboxEventType,
    RunEvaluationRequested,
)


class OutboxMessageMapper:
    @staticmethod
    def map_run_evaluation_message(
        submission: Submission, id: UUID, evaluation_id: UUID
    ) -> OutboxMessage:
        run_evaluation_event = RunEvaluationRequested(
            evaluation_id=evaluation_id,
            submission_id=submission.id,
            assignment_id=submission.assignment_id,
            language=submission.language,
            code=submission.code,
        )
        return OutboxMessage(
            id=id,
            event_type=OutboxEventType.RUN_EVALUATION_REQUESTED,
            payload=run_evaluation_event,
        )
