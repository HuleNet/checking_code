from uuid import UUID

from sqlalchemy import insert, select, update, case
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from checking_service.domain.entities import ExecutionCase
from checking_service.application.models.pagination import CursorPagination, Page
from checking_service.application.ports.repositories import ExecutionCaseRepository
from checking_service.infrastructure.db.models import ExecutionCaseORM
from checking_service.infrastructure.db.models.mappers import ExecutionCaseMapper
from checking_service.infrastructure.errors import (
    RepositoryIntegrityError,
    InternalRepositoryError,
)


class SQLAlchemyExecutionCaseRepository(ExecutionCaseRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.model = ExecutionCaseORM

    async def add_many(
        self, execution_cases: list[ExecutionCase]
    ) -> list[ExecutionCase]:
        if not execution_cases:
            return []

        values = [
            ExecutionCaseMapper.to_dict(domain=execution_case)
            for execution_case in execution_cases
        ]
        query = insert(self.model).values(values)

        try:
            await self.session.execute(query)

        except IntegrityError as exc:
            raise RepositoryIntegrityError(
                message="Bulk insert ExecutionCases failed",
                details={
                    "execution_cases_count": len(execution_cases),
                },
            ) from exc

        except SQLAlchemyError as exc:
            raise InternalRepositoryError(
                message="Database error",
                details={},
            ) from exc

        return execution_cases

    async def get(self, id: UUID) -> ExecutionCase | None:
        query = select(self.model).where(self.model.id == id)

        try:
            orm_result = await self.session.execute(query)

        except SQLAlchemyError as exc:
            raise InternalRepositoryError(
                message="Database error",
                details={},
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
            raise InternalRepositoryError(
                message="Database error",
                details={},
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
            raise InternalRepositoryError(
                message="Database error",
                details={},
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

    async def update_many(
        self, execution_cases: list[ExecutionCase]
    ) -> list[ExecutionCase]:
        if not execution_cases:
            return []

        ids = [execution_case.id for execution_case in execution_cases]
        query = (
            update(self.model)
            .where(self.model.id.in_(ids))
            .values(
                status=case(
                    {execution_case.id: execution_case.status for execution_case in execution_cases},
                    value=self.model.id,
                ),
                stdout=case(
                    {execution_case.id: execution_case.stdout for execution_case in execution_cases},
                    value=self.model.id,
                ),
                stderr=case(
                    {execution_case.id: execution_case.stderr for execution_case in execution_cases},
                    value=self.model.id,
                ),
                execution_time_ms=case(
                    {execution_case.id: execution_case.execution_time_ms for execution_case in execution_cases},
                    value=self.model.id,
                ),
            )
        )

        try:
            await self.session.execute(query)

        except SQLAlchemyError as exc:
            raise InternalRepositoryError(
                message="Database error",
                details={},
            ) from exc

        return execution_cases
