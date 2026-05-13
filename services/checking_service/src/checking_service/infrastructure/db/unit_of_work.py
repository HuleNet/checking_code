from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

from checking_service.application.ports import UnitOfWork
from checking_service.infrastructure.db.repositories import (
    SQLAlchemyEvaluationRepository,
    SQLAlchemyExecutionCaseRepository,
    SQLAlchemyTestCaseRepository,
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
