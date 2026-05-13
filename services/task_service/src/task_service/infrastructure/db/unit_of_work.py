from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

from task_service.application.ports import UnitOfWork
from task_service.infrastructure.db.repositories import (
    SQLAlchemyAssignmentRepository,
    SQLAlchemyGroupAssignmentRepository,
    SQLAlchemySubmissionRepository,
    SQLAlchemyFinalResultRepository,
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
