from typing import Any

from checking_service.application.models.outbox import OutboxMessage
from checking_service.infrastructure.db.models import OutboxMessageORM


class OutboxMessageMapper:
    @staticmethod
    def to_app_model(orm: OutboxMessageORM) -> OutboxMessage:
        return OutboxMessage(
            id=orm.id,
            event_type=orm.event_type,
            payload=orm.payload,
            status=orm.status,
            created_at=orm.created_at,
            published_at=orm.published_at,
            retry_count=orm.retry_count,
            next_attempt_at=orm.next_attempt_at,
        )

    @staticmethod
    def to_dict(app_model: OutboxMessage) -> dict[str, Any]:
        return {
            "id": app_model.id,
            "event_type": app_model.event_type,
            "payload": app_model.payload,
            "status": app_model.status,
            "created_at": app_model.created_at,
            "published_at": app_model.published_at,
            "retry_count": app_model.retry_count,
            "next_attempt_at": app_model.next_attempt_at,
        }
