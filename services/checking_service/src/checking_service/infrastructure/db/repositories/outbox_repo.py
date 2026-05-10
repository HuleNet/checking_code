from uuid import UUID
from datetime import datetime, timezone

from sqlalchemy import insert, select, update
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from checking_service.application.models.outbox import OutboxMessage
from checking_service.application.ports.repositories import OutboxRepository
from checking_service.infrastructure.db.models import OutboxMessageORM
from checking_service.infrastructure.db.models.mappers import OutboxMessageMapper
from checking_service.infrastructure.errors import (
    RepositoryIntegrityError,
    RepositoryInternalError,
)


class SQLAlchemyOutboxRepository(OutboxRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.model = OutboxMessageORM

    async def add(self, message: OutboxMessage) -> None:
        query = insert(self.model).values(
            **OutboxMessageMapper.to_dict(app_model=message)
        )

        try:
            await self.session.execute(query)

        except IntegrityError as exc:
            raise RepositoryIntegrityError(
                message="OutboxMessage already exists",
                details={
                    "entity": "outbox_message",
                    "operation": "add",
                    "id": message.id,
                },
            ) from exc

        except SQLAlchemyError as exc:
            raise RepositoryInternalError(
                message="Failed to insert OutboxMessage",
                details={
                    "entity": "outbox_message",
                    "operation": "add",
                    "id": message.id,
                },
            ) from exc

    async def get_unprocessed(
        self,
        batch_size: int,
    ) -> list[OutboxMessage]:
        query = (
            select(self.model)
            .where(self.model.processed_at.is_(None))
            .order_by(self.model.occurred_at)
            .limit(batch_size)
        )

        try:
            orm_results = await self.session.execute(query)

        except SQLAlchemyError as exc:
            raise RepositoryInternalError(
                message="Failed to fetch unprocessed OutboxMessages",
                details={
                    "entity": "outbox_message",
                    "operation": "get_unprocessed",
                    "batch_size": batch_size,
                },
            ) from exc

        return [
            OutboxMessageMapper.to_app_model(orm=orm)
            for orm in orm_results.scalars().all()
        ]

    async def mark_processed(
        self,
        ids: list[UUID],
    ) -> None:
        if not ids:
            return

        query = (
            update(self.model)
            .where(self.model.id.in_(ids))
            .values(processed_at=datetime.now(timezone.utc))
        )

        try:
            await self.session.execute(query)

        except IntegrityError as exc:
            raise RepositoryIntegrityError(
                message="Failed to mark OutboxMessages as processed",
                details={
                    "entity": "outbox_message",
                    "operation": "mark_processed",
                    "ids": ids,
                },
            ) from exc

        except SQLAlchemyError as exc:
            raise RepositoryInternalError(
                message="Failed to mark OutboxMessages as processed",
                details={
                    "entity": "outbox_message",
                    "operation": "mark_processed",
                    "ids": ids,
                },
            ) from exc
