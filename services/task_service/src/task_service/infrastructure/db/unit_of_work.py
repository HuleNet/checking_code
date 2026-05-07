from typing import Any

from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

from task_service.domain.events import DomainEvent
from task_service.application.models.outbox import OutboxMessage
from task_service.application.dto.mappers import EventMapper
from task_service.application.ports import UnitOfWork
from task_service.infrastructure.db.repositories import (
    SQLAlchemyAssignmentRepository,
    SQLAlchemyGroupAssignmentRepository,
    SQLAlchemySubmissionRepository,
    SQLAlchemyFinalResultRepository,
    SQLAlchemyOutboxRepository,
)
from task_service.infrastructure.errors import RepositoryInternalError


class SQLAlchemyUnitOfWork(UnitOfWork):
    def __init__(
        self,
        session_factory: async_sessionmaker[AsyncSession],
    ) -> None:
        self.session_factory = session_factory
        self.session: AsyncSession | None = None

    async def __aenter__(self) -> "SQLAlchemyUnitOfWork":
        self.session = self.session_factory()
        self.assignment_repo = SQLAlchemyAssignmentRepository(session=self.session)
        self.group_assignment_repo = SQLAlchemyGroupAssignmentRepository(
            session=self.session
        )
        self.submission_repo = SQLAlchemySubmissionRepository(session=self.session)
        self.final_result_repo = SQLAlchemyFinalResultRepository(session=self.session)
        self.outbox_repo = SQLAlchemyOutboxRepository(session=self.session)
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        if self.session is None:
            return

        if exc:
            await self.rollback()

        await self.session.close()

    async def commit(self) -> None:
        if self.session is None:
            raise RepositoryInternalError(
                message="Session is not initialized",
                details={
                    "entity": "unit_of_work",
                    "operation": "commit",
                },
            )

        await self.session.commit()

    async def rollback(self) -> None:
        if self.session is None:
            raise RepositoryInternalError(
                message="Session is not initialized",
                details={
                    "entity": "unit_of_work",
                    "operation": "rollback",
                },
            )

        await self.session.rollback()

    async def track(self, entity: Any) -> None:
        if self.session is None:
            raise RepositoryInternalError(
                message="Session is not initialized",
                details={
                    "entity": "unit_of_work",
                    "operation": "track",
                },
            )

        events: list[DomainEvent] = getattr(entity, "events", [])

        if not events:
            return

        for event in events:
            outbox_message = OutboxMessage(
                id=event.id,
                event_type=event.__class__.__name__,
                payload=EventMapper.serialize_event(event=event),
                occurred_at=event.occurred_at,
            )
            await self.outbox_repo.add(message=outbox_message)

        entity.clear_events()
