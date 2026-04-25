from uuid import UUID
from datetime import datetime, timezone

from sqlalchemy import insert, select, update
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from checking_service.application.models.enums import OutboxStatus
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
                    "operation": "insert",
                    "id": message.id,
                },
            ) from exc

        except SQLAlchemyError as exc:
            raise RepositoryInternalError(
                message="Failed to insert OutboxMessage",
                details={
                    "entity": "outbox_message",
                    "operation": "insert",
                    "id": message.id,
                },
            ) from exc

    async def claim_batch(self, limit: int) -> list[OutboxMessage]:
        subquery = (
            select(self.model.id)
            .where(self.model.status == OutboxStatus.PENDING)
            .order_by(self.model.created_at)
            .limit(limit)
            .scalar_subquery()
        )
        query = (
            update(self.model)
            .where(self.model.id.in_(subquery))
            .values(status=OutboxStatus.PROCESSING)
            .returning(self.model)
        )

        try:
            orm_results = await self.session.execute(query)

        except SQLAlchemyError as exc:
            raise RepositoryInternalError(
                message="Failed to claim OutboxMessage",
                details={
                    "entity": "outbox_message",
                    "operation": "claim_batch",
                    "limit": limit,
                },
            ) from exc

        return [
            OutboxMessageMapper.to_app_model(orm=orm)
            for orm in orm_results.scalars().all()
        ]

    async def mark_published(self, id: UUID) -> None:
        query = (
            update(self.model)
            .where(self.model.id == id, self.model.status == OutboxStatus.PROCESSING)
            .values(
                status=OutboxStatus.PUBLISHED,
                published_at=datetime.now(timezone.utc),
            )
            .returning(self.model)
        )

        try:
            orm_result = await self.session.execute(query)

        except SQLAlchemyError as exc:
            raise RepositoryInternalError(
                message="Failed to mark OutboxMessage as published",
                details={
                    "entity": "outbox_message",
                    "operation": "mark_published",
                    "id": id,
                },
            ) from exc

        orm = orm_result.scalar_one_or_none()

        if orm is None:
            raise RepositoryIntegrityError(
                message="OutboxMessage not found or invalid state",
                details={
                    "entity": "outbox_message",
                    "operation": "mark_published",
                    "id": id,
                    "expected_status": OutboxStatus.PROCESSING.value,
                    "reason": "stale_state_or_not_found",
                },
            )

    async def mark_failed(self, id: UUID) -> None:
        query = (
            update(self.model)
            .where(self.model.id == id, self.model.status == OutboxStatus.PROCESSING)
            .values(
                status=OutboxStatus.FAILED,
                retry_count=self.model.retry_count + 1,
            )
            .returning(self.model)
        )

        try:
            orm_result = await self.session.execute(query)

        except SQLAlchemyError as exc:
            raise RepositoryInternalError(
                message="Failed to mark OutboxMessage as failed",
                details={
                    "entity": "outbox_message",
                    "operation": "mark_failed",
                    "id": id,
                },
            ) from exc

        orm = orm_result.scalar_one_or_none()

        if orm is None:
            raise RepositoryIntegrityError(
                message="OutboxMessage not found or invalid state",
                details={
                    "entity": "outbox_message",
                    "operation": "mark_failed",
                    "id": id,
                    "expected_status": OutboxStatus.PROCESSING.value,
                    "reason": "stale_state_or_not_found",
                },
            )
