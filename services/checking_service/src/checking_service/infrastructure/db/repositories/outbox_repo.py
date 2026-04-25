from uuid import UUID
from random import uniform
from datetime import datetime, timezone, timedelta

from sqlalchemy import insert, select, update, case, or_
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
from checking_service.infrastructure.core import get_settings_cached


def calc_backoff(retry_count: int) -> timedelta:
    base_delay = get_settings_cached().retry_base_delay_sec
    max_delay = get_settings_cached().retry_max_delay_sec
    delay = min(max_delay, base_delay * (2**1.5))
    delay = uniform(delay * 0.5, delay * 1.5)
    return timedelta(seconds=delay)


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

    async def claim_batch(self, batch_size: int) -> list[OutboxMessage]:
        subquery = (
            select(self.model.id)
            .where(
                self.model.status == OutboxStatus.PENDING,
                or_(
                    self.model.next_attempt_at.is_(None),
                    self.model.next_attempt_at <= datetime.now(timezone.utc),
                ),
            )
            .limit(batch_size)
            .with_for_update(skip_locked=True)
        )
        query = (
            update(self.model)
            .where(self.model.id.in_(subquery))
            .values(
                status=OutboxStatus.PROCESSING,
            )
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
                    "batch_size": batch_size,
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
                retry_count=self.model.retry_count + 1,
                status=case(
                    (
                        self.model.retry_count + 1
                        >= get_settings_cached().outbox_max_retries,
                        OutboxStatus.FAILED,
                    ),
                    else_=OutboxStatus.PENDING,
                ),
                next_attempt_at=datetime.now(timezone.utc)
                + calc_backoff(self.model.retry_count),  # type: ignore
            )
            .returning(self.model)
        )

        try:
            orm_results = await self.session.execute(query)

        except SQLAlchemyError as exc:
            raise RepositoryInternalError(
                message="Failed to mark OutboxMessage as failed",
                details={
                    "entity": "outbox_message",
                    "operation": "mark_failed",
                    "id": id,
                },
            ) from exc

        orm = orm_results.scalar_one_or_none()

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

    async def mark_failed_permanently(self, id: UUID) -> None:
        query = (
            update(self.model)
            .where(self.model.id == id)
            .values(status=OutboxStatus.FAILED)
            .returning(self.model)
        )

        try:
            orm_result = await self.session.execute(query)

        except SQLAlchemyError as exc:
            raise RepositoryInternalError(
                message="Failed to mark OutboxMessage as permanently failed",
                details={
                    "entity": "outbox_message",
                    "operation": "mark_failed_permanently",
                    "id": id,
                },
            ) from exc

        orm = orm_result.scalar_one_or_none()

        if orm is None:
            raise RepositoryIntegrityError(
                message="OutboxMessage not found",
                details={
                    "entity": "outbox_message",
                    "operation": "mark_failed_permanently",
                    "id": id,
                },
            )
