from celery import Celery

from task_service.application.models.outbox import OutboxMessage
from task_service.infrastructure.broker.celery_app import celery_app


class EventPublisher:
    def __init__(self, app: Celery) -> None:
        self.app = app

    def publish(self, message: OutboxMessage) -> None:
        self.app.send_task(
            name=message.event_type,
            kwargs=message.payload,
        )


publisher = EventPublisher(app=celery_app)
