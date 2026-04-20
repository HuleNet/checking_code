from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

from checking_service.application.ports import UnitOfWork
from checking_service.infrastructure.db.repositories import (
    SQLAlchemyEvaluationRepository,
    SQLAlchemyExecutionCaseRepository,
    SQLAlchemyInputCaseRepository,
    SQLAlchemyOutboxRepository,
)


class SQLAlchemyUnitOfWork(UnitOfWork):
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]):
        self._session_factory = session_factory
        self.session: AsyncSession | None = None

    async def __aenter__(self) -> "SQLAlchemyUnitOfWork":
        self.session = self._session_factory()
        self.evaluation_repo = SQLAlchemyEvaluationRepository(session=self.session)
        self.execution_case_repo = SQLAlchemyExecutionCaseRepository(
            session=self.session
        )
        self.input_case_repo = SQLAlchemyInputCaseRepository(session=self.session)
        self.outbox_repo = SQLAlchemyOutboxRepository(session=self.session)
        return self

    async def __aexit__(self, exc_type, exc, tb):
        if exc_type:
            await self.rollback()
        else:
            pass

        await self.session.close()

    async def commit(self) -> None:
        if self.session is None:
            raise RuntimeError("Uow is not entered")

        try:
            await self.session.commit()
        except Exception:
            await self.session.rollback()
            raise

    async def rollback(self) -> None:
        if self.session is None:
            raise RuntimeError("Uow is not entered")

        await self.session.rollback()
