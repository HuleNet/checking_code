from uuid import UUID

from sqlalchemy import insert, select, update
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from task_service.application.models.outbox import OutboxMessage
from task_service.application.ports.repositories import OutboxRepository
from task_service.infrastructure.db.models import OutboxMessageORM
from task_service.infrastructure.db.models.mappers import OutboxMessageMapper
from task_service.infrastructure.errors import (
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

    async def get_unprocessed(self, limit: int) -> list[OutboxMessage]:
        query = select(self.model).where(self.model.processed.is_(False)).limit(limit)

        try:
            orm_results = await self.session.execute(query)

        except SQLAlchemyError as exc:
            raise RepositoryInternalError(
                message="Failed to fetch unprocessed OutboxMessages",
                details={
                    "entity": "outbox_message",
                    "operation": "get_unprocessed",
                },
            ) from exc

        return [
            OutboxMessageMapper.to_app_model(orm=orm)
            for orm in orm_results.scalars().all()
        ]

    async def mark_processed(self, id: UUID) -> None:
        query = (
            update(self.model)
            .where(self.model.id == id)
            .values(processed=True)
            .returning(self.model)
        )

        try:
            orm_result = await self.session.execute(query)

        except IntegrityError as exc:
            raise RepositoryIntegrityError(
                message="Failed to mark OutboxMessage as processed",
                details={
                    "entity": "outbox_message",
                    "operation": "mark_processed",
                    "id": id,
                },
            ) from exc

        except SQLAlchemyError as exc:
            raise RepositoryInternalError(
                message="Failed to mark OutboxMessage as processed",
                details={
                    "entity": "outbox_message",
                    "operation": "mark_processed",
                    "id": id,
                },
            ) from exc

        orm = orm_result.scalar_one_or_none()

        if orm is None:
            raise RepositoryIntegrityError(
                message="OutboxMessage not found",
                details={
                    "entity": "outbox_message",
                    "operation": "mark_processed",
                    "id": id,
                },
            )
