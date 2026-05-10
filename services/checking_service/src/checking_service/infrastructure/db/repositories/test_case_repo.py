from uuid import UUID

from sqlalchemy import insert, select, update, delete
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from checking_service.domain.entities import TestCase
from checking_service.application.models.pagination import CursorPagination, Page
from checking_service.application.ports.repositories import TestCaseRepository
from checking_service.infrastructure.db.models import TestCaseORM
from checking_service.infrastructure.db.models.mappers import TestCaseMapper
from checking_service.infrastructure.errors import (
    RepositoryIntegrityError,
    RepositoryInternalError,
)


class SQLAlchemyTestCaseRepository(TestCaseRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.model = TestCaseORM

    async def add(self, test_case: TestCase) -> TestCase:
        query = (
            insert(self.model)
            .values(**TestCaseMapper.to_dict(domain=test_case))
            .returning(self.model)
        )

        try:
            orm_result = await self.session.execute(query)

        except IntegrityError as exc:
            raise RepositoryIntegrityError(
                message="TestCase already exists",
                details={
                    "entity": "test_case",
                    "operation": "add",
                    "id": test_case.id,
                },
            ) from exc

        except SQLAlchemyError as exc:
            raise RepositoryInternalError(
                message="Failed to insert TestCase",
                details={
                    "entity": "test_case",
                    "operation": "add",
                    "id": test_case.id,
                },
            ) from exc

        orm = orm_result.scalar_one()
        return TestCaseMapper.to_domain(orm=orm)

    async def get(self, id: UUID) -> TestCase | None:
        query = select(self.model).where(self.model.id == id)

        try:
            orm_result = await self.session.execute(query)

        except SQLAlchemyError as exc:
            raise RepositoryInternalError(
                message="Failed to fetch TestCase",
                details={
                    "entity": "test_case",
                    "operation": "get",
                    "id": id,
                },
            ) from exc

        orm = orm_result.scalar_one_or_none()

        if orm is None:
            return None

        return TestCaseMapper.to_domain(orm=orm)

    async def get_by_assignment(self, assignment_id: UUID) -> list[TestCase]:
        query = select(self.model).where(self.model.assignment_id == assignment_id)

        try:
            orm_results = await self.session.execute(query)

        except SQLAlchemyError as exc:
            raise RepositoryInternalError(
                message="Failed to fetch InputCases by assignment",
                details={
                    "entity": "test_case",
                    "operation": "get_by_assignment",
                    "assignment_id": assignment_id,
                },
            ) from exc

        return [
            TestCaseMapper.to_domain(orm=orm) for orm in orm_results.scalars().all()
        ]

    async def get_page(
        self, assignment_id: UUID, pagination: CursorPagination
    ) -> Page[TestCase]:
        query = select(self.model).where(self.model.assignment_id == assignment_id)

        if pagination.cursor:
            query = query.where(self.model.id > pagination.cursor["id"])

        query = query.order_by(self.model.id).limit(pagination.limit + 1)

        try:
            orm_results = await self.session.execute(query)

        except SQLAlchemyError as exc:
            raise RepositoryInternalError(
                message="Failed to fetch TestCase page",
                details={
                    "entity": "test_case",
                    "operation": "get_page",
                    "assignment_id": assignment_id,
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
            items=[TestCaseMapper.to_domain(orm=orm) for orm in orms],
            next_cursor=next_cursor,
        )

    async def update(self, test_case: TestCase) -> TestCase:
        query = (
            update(self.model)
            .where(self.model.id == test_case.id)
            .values(
                input_data=test_case.input_data,
                expected_output=test_case.expected_output,
                check_type=test_case.check_type,
            )
            .returning(self.model)
        )

        try:
            orm_result = await self.session.execute(query)

        except IntegrityError as exc:
            raise RepositoryIntegrityError(
                message="Failed to update TestCase",
                details={
                    "entity": "test_case",
                    "operation": "update",
                    "id": test_case.id,
                    "input_data": test_case.input_data,
                    "expected_output": test_case.expected_output,
                    "check_type": test_case.check_type.value,
                },
            ) from exc

        except SQLAlchemyError as exc:
            raise RepositoryInternalError(
                message="Failed to update TestCase",
                details={
                    "entity": "test_case",
                    "operation": "update",
                    "id": test_case.id,
                },
            ) from exc

        orm = orm_result.scalar_one()
        return TestCaseMapper.to_domain(orm=orm)

    async def delete(self, id: UUID) -> TestCase | None:
        query = delete(self.model).where(self.model.id == id).returning(self.model)

        try:
            orm_result = await self.session.execute(query)

        except SQLAlchemyError as exc:
            raise RepositoryInternalError(
                message="Failed to delete TestCase",
                details={
                    "entity": "test_case",
                    "operation": "delete",
                    "id": id,
                },
            ) from exc

        orm = orm_result.scalar_one_or_none()

        if orm is None:
            return None

        return TestCaseMapper.to_domain(orm=orm)
