from checking_service.application.models.outbox import OutboxMessage
from checking_service.infrastructure.errors import TransientError
from checking_service.infrastructure.core import celery_app


class CeleryDispatcher:
    async def dispatch(self, message: OutboxMessage) -> None:
        try:
            celery_app.send_task(
                name=message.event_type,
                kwargs=message.payload,
            )

        except Exception as exc:
            raise TransientError("Failed to dispatch message") from exc
