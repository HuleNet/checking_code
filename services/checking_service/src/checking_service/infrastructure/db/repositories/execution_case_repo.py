from uuid import UUID

from sqlalchemy import insert, select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from checking_service.domain.entities import ExecutionCase
from checking_service.application.models.pagination import CursorPagination, Page
from checking_service.application.ports.repositories import ExecutionCaseRepository
from checking_service.infrastructure.db.models import ExecutionCaseORM
from checking_service.infrastructure.db.models.mappers import ExecutionCaseMapper
from checking_service.infrastructure.errors import (
    RepositoryIntegrityError,
    RepositoryInternalError,
)


class SQLAlchemyExecutionCaseRepository(ExecutionCaseRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.model = ExecutionCaseORM

    async def add_many(self, execution_cases: list[ExecutionCase]) -> None:
        if not execution_cases:
            return

        values = [
            ExecutionCaseMapper.to_dict(domain=execution_case)
            for execution_case in execution_cases
        ]
        query = insert(self.model).values(values)

        try:
            await self.session.execute(query)

        except IntegrityError as exc:
            raise RepositoryIntegrityError(
                message="Some of ExecutionCases already exist",
                details={
                    "entity": "execution_case",
                    "operation": "add_many",
                    "execution_cases_count": len(execution_cases),
                },
            ) from exc

        except SQLAlchemyError as exc:
            raise RepositoryInternalError(
                message="Failed to bulk insert ExecutionCases",
                details={
                    "entity": "execution_case",
                    "operation": "add_many",
                    "execution_cases_count": len(execution_cases),
                },
            ) from exc

    async def get(self, id: UUID) -> ExecutionCase | None:
        query = select(self.model).where(self.model.id == id)

        try:
            orm_result = await self.session.execute(query)

        except SQLAlchemyError as exc:
            raise RepositoryInternalError(
                message="Failed to fetch ExecutionCase",
                details={
                    "entity": "execution_case",
                    "operation": "get",
                    "id": id,
                },
            ) from exc

        orm = orm_result.scalar_one_or_none()

        if orm is None:
            return None

        return ExecutionCaseMapper.to_domain(orm=orm)

    async def get_by_evaluation(self, evaluation_id: UUID) -> list[ExecutionCase]:
        query = select(self.model).where(self.model.evaluation_id == evaluation_id)

        try:
            orm_results = await self.session.execute(query)

        except SQLAlchemyError as exc:
            raise RepositoryInternalError(
                message="Failed to fetch ExecutionCases by evaluation",
                details={
                    "entity": "execution_case",
                    "operation": "get_by_evaluation",
                    "evaluation_id": evaluation_id,
                },
            ) from exc

        return [
            ExecutionCaseMapper.to_domain(orm=orm)
            for orm in orm_results.scalars().all()
        ]

    async def get_page(
        self, evaluation_id: UUID, pagination: CursorPagination
    ) -> Page[ExecutionCase]:
        query = select(self.model).where(self.model.evaluation_id == evaluation_id)

        if pagination.cursor:
            query = query.where(self.model.id > pagination.cursor["id"])

        query = query.order_by(self.model.id).limit(pagination.limit + 1)

        try:
            orm_results = await self.session.execute(query)

        except SQLAlchemyError as exc:
            raise RepositoryInternalError(
                message="Failed to fetch ExecutionCase page",
                details={
                    "entity": "execution_case",
                    "operation": "get_page",
                    "evaluation": evaluation_id,
                    "limit": pagination.limit,
                    "cursor": pagination.cursor,
                },
            ) from exc

        orms = orm_results.scalars().all()
        has_next = len(orms) > pagination.limit
        orms = orms[: pagination.limit]

        if has_next:
            last = orms[-1]
            next_cursor = {"id": last.id}
        else:
            next_cursor = None

        return Page(
            items=[ExecutionCaseMapper.to_domain(orm=orm) for orm in orms],
            next_cursor=next_cursor,
        )
