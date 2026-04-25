from uuid import UUID

from sqlalchemy import insert, select, update, delete
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from checking_service.domain.entities import InputCase
from checking_service.application.models.pagination import CursorPagination, Page
from checking_service.application.ports.repositories import InputCaseRepository
from checking_service.infrastructure.db.models import InputCaseORM
from checking_service.infrastructure.db.models.mappers import InputCaseMapper
from checking_service.infrastructure.errors import (
    RepositoryIntegrityError,
    RepositoryInternalError,
)


class SQLAlchemyInputCaseRepository(InputCaseRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.model = InputCaseORM

    async def add(self, input_case: InputCase) -> InputCase:
        query = (
            insert(self.model)
            .values(**InputCaseMapper.to_dict(domain=input_case))
            .returning(self.model)
        )

        try:
            orm_result = await self.session.execute(query)

        except IntegrityError as exc:
            raise RepositoryIntegrityError(
                message="InputCase already exists",
                details={
                    "entity": "input_case",
                    "operation": "insert",
                    "id": input_case.id,
                },
            ) from exc

        except SQLAlchemyError as exc:
            raise RepositoryInternalError(
                message="Failed to insert InputCase",
                details={
                    "entity": "input_case",
                    "operation": "insert",
                    "id": input_case.id,
                },
            ) from exc

        orm = orm_result.scalar_one()
        return InputCaseMapper.to_domain(orm=orm)

    async def get(self, id: UUID) -> InputCase | None:
        query = select(self.model).where(self.model.id == id)

        try:
            orm_result = await self.session.execute(query)

        except SQLAlchemyError as exc:
            raise RepositoryInternalError(
                message="Failed to fetch InputCase",
                details={
                    "entity": "input_case",
                    "operation": "get",
                    "id": id,
                },
            ) from exc

        orm = orm_result.scalar_one_or_none()

        if orm is None:
            return None

        return InputCaseMapper.to_domain(orm=orm)

    async def get_by_assignment(self, assignment_id: UUID) -> list[InputCase]:
        query = select(self.model).where(self.model.assignment_id == assignment_id)

        try:
            orm_results = await self.session.execute(query)

        except SQLAlchemyError as exc:
            raise RepositoryInternalError(
                message="Failed to fetch InputCases by assignment",
                details={
                    "entity": "input_case",
                    "operation": "get_by_assignment",
                    "assignment_id": assignment_id,
                },
            ) from exc

        return [
            InputCaseMapper.to_domain(orm=orm) for orm in orm_results.scalars().all()
        ]

    async def get_page(
        self, assignment_id: UUID, pagination: CursorPagination
    ) -> Page[InputCase]:
        query = select(self.model).where(self.model.assignment_id == assignment_id)

        if pagination.cursor:
            query = query.where(self.model.id > pagination.cursor["id"])

        query = query.order_by(self.model.id).limit(pagination.limit + 1)

        try:
            orm_results = await self.session.execute(query)

        except SQLAlchemyError as exc:
            raise RepositoryInternalError(
                message="Failed to fetch InputCase page",
                details={
                    "entity": "input_case",
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
            items=[InputCaseMapper.to_domain(orm=orm) for orm in orms],
            next_cursor=next_cursor,
        )

    async def update(self, input_case: InputCase) -> InputCase:
        query = (
            update(self.model)
            .where(self.model.id == input_case.id)
            .values(
                input_data=input_case.input_data,
                expected_output=input_case.expected_output,
                check_type=input_case.check_type,
            )
            .returning(self.model)
        )

        try:
            orm_result = await self.session.execute(query)

        except IntegrityError as exc:
            raise RepositoryIntegrityError(
                message="Failed to update InputCase",
                details={
                    "entity": "input_case",
                    "operation": "update",
                    "id": input_case.id,
                    "input_data": input_case.input_data,
                    "expected_output": input_case.expected_output,
                    "check_type": input_case.check_type.value,
                },
            ) from exc

        except SQLAlchemyError as exc:
            raise RepositoryInternalError(
                message="Failed to update InputCase",
                details={
                    "entity": "input_case",
                    "operation": "update",
                    "id": input_case.id,
                },
            ) from exc

        orm = orm_result.scalar_one()
        return InputCaseMapper.to_domain(orm=orm)

    async def delete(self, id: UUID) -> InputCase | None:
        query = delete(self.model).where(self.model.id == id).returning(self.model)

        try:
            orm_result = await self.session.execute(query)

        except SQLAlchemyError as exc:
            raise RepositoryInternalError(
                message="Failed to delete InputCase",
                details={
                    "entity": "input_case",
                    "operation": "delete",
                    "id": id,
                },
            ) from exc

        orm = orm_result.scalar_one_or_none()

        if orm is None:
            return None

        return InputCaseMapper.to_domain(orm=orm)
