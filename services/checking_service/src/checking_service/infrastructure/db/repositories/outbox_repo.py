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
    InternalRepositoryError,
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
                message="Outbox message already exists",
                details={"id": message.id},
            ) from exc

        except SQLAlchemyError as exc:
            raise InternalRepositoryError(
                message="Database error",
                details={},
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
            raise InternalRepositoryError(
                message="Database error",
                details={},
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
        )

        try:
            query_result = await self.session.execute(query)

        except SQLAlchemyError as exc:
            raise InternalRepositoryError(
                message="Database error",
                details={"id": id},
            ) from exc

        if query_result.rowcount == 0:  # type: ignore[attr-defined]
            raise RepositoryIntegrityError(
                message="Outbox message not in processing state",
                details={
                    "id": id,
                    "reason": "invalid_state_transition",
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
        )

        try:
            query_result = await self.session.execute(query)

        except SQLAlchemyError as exc:
            raise InternalRepositoryError(
                message="Database error",
                details={"id": id},
            ) from exc

        if query_result.rowcount == 0:  # type: ignore[attr-defined]
            raise RepositoryIntegrityError(
                message="Outbox message not in processing state",
                details={
                    "id": id,
                    "reason": "invalid_state_transition",
                },
            )
