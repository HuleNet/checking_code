from checking_service.application.models.outbox import OutboxMessage
from checking_service.infrastructure.core import celery_app


class CeleryDispatcher:
    def dispatch(self, message: OutboxMessage) -> None:
        if message.event_type == "RUN_EVALUATION_REQUESTED":
            celery_app.send_task("run_evaluation", kwargs=message.payload)

        else:
            raise ValueError(f"Unknown event type: {message.event_type}")
