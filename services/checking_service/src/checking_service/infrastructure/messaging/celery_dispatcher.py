from logging import getLogger

from checking_service.application.models.outbox import OutboxMessage
from checking_service.infrastructure.errors import TransientError
from checking_service.infrastructure.core import celery_app


logger = getLogger(__name__)


class CeleryDispatcher:
    async def dispatch(self, message: OutboxMessage) -> None:
        try:
            logger.info(
                "dispatch_task",
                extra={
                    "extra": {
                        "event_type": message.event_type,
                        "message_id": str(message.id),
                    },
                },
            )
            celery_app.send_task(
                name=message.event_type,
                kwargs=message.payload,
            )

        except Exception as exc:
            logger.exception(
                "dispatch_failed",
                extra={
                    "extra": {
                        "event_type": message.event_type,
                        "message_id": str(message.id),
                    }
                },
            )
            raise TransientError("Failed to dispatch message") from exc
