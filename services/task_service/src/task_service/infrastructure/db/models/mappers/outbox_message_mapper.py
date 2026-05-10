from typing import Any

from task_service.application.models.outbox import OutboxMessage
from task_service.infrastructure.db.models import OutboxMessageORM


class OutboxMessageMapper:
    @staticmethod
    def to_app_model(orm: OutboxMessageORM) -> OutboxMessage:
        return OutboxMessage(
            id=orm.id,
            event_type=orm.event_type,
            payload=orm.payload,
            occurred_at=orm.occurred_at,
            processed_at=orm.processed_at,
        )

    @staticmethod
    def to_dict(app_model: OutboxMessage) -> dict[str, Any]:
        return {
            "id": app_model.id,
            "event_type": app_model.event_type,
            "payload": app_model.payload,
            "occurred_at": app_model.occurred_at,
            "processed_at": app_model.processed_at,
        }
