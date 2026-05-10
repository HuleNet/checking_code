from typing import Any

from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

from checking_service.domain.events import DomainEvent
from checking_service.application.dto.mappers import EventMapper
from checking_service.application.models.outbox import OutboxMessage
from checking_service.application.ports import UnitOfWork
from checking_service.infrastructure.db.repositories import (
    SQLAlchemyEvaluationRepository,
    SQLAlchemyExecutionCaseRepository,
    SQLAlchemyTestCaseRepository,
    SQLAlchemyOutboxRepository,
)
from checking_service.infrastructure.errors import RepositoryInternalError


class SQLAlchemyUnitOfWork(UnitOfWork):
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self._session_factory = session_factory
        self.session: AsyncSession | None = None

    async def __aenter__(self) -> "SQLAlchemyUnitOfWork":
        self.session = self._session_factory()
        self.evaluation_repo = SQLAlchemyEvaluationRepository(session=self.session)
        self.execution_case_repo = SQLAlchemyExecutionCaseRepository(
            session=self.session
        )
        self.test_case_repo = SQLAlchemyTestCaseRepository(session=self.session)
        self.outbox_repo = SQLAlchemyOutboxRepository(session=self.session)
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        if self.session is None:
            return

        if exc_type:
            await self.rollback()
        else:
            pass

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

        try:
            await self.session.commit()
        except Exception:
            await self.session.rollback()
            raise

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

        pull_events = getattr(entity, "pull_events", None)

        if pull_events is None:
            return

        events: list[DomainEvent] = pull_events()

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
