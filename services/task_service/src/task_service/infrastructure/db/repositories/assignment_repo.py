from uuid import UUID

from sqlalchemy import insert, select, update, delete
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from task_service.domain.entities import Assignment
from task_service.application.models.pagination import CursorPagination, Page
from task_service.application.ports.repositories import AssignmentRepository
from task_service.infrastructure.db.models import AssignmentORM
from task_service.infrastructure.db.models.mappers import AssignmentMapper
from task_service.infrastructure.errors import (
    RepositoryIntegrityError,
    RepositoryInternalError,
)


class SQLAlchemyAssignmentRepository(AssignmentRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.model = AssignmentORM

    async def add(self, assignment: Assignment) -> Assignment:
        query = (
            insert(self.model)
            .values(**AssignmentMapper.to_dict(domain=assignment))
            .returning(self.model)
        )

        try:
            orm_result = await self.session.execute(query)

        except IntegrityError as exc:
            raise RepositoryIntegrityError(
                message="Assignment already exists",
                details={
                    "entity": "assignment",
                    "operation": "add",
                    "id": assignment.id,
                },
            ) from exc

        except SQLAlchemyError as exc:
            raise RepositoryInternalError(
                message="Failed to insert Assignment",
                details={
                    "entity": "assignment",
                    "operation": "add",
                    "id": assignment.id,
                },
            ) from exc

        orm = orm_result.scalar_one()
        return AssignmentMapper.to_domain(orm=orm)

    async def get(self, id: UUID) -> Assignment | None:
        query = select(self.model).where(self.model.id == id)

        try:
            orm_result = await self.session.execute(query)

        except SQLAlchemyError as exc:
            raise RepositoryInternalError(
                message="Failed to fetch Assignment",
                details={
                    "entity": "assignment",
                    "operation": "get",
                    "id": id,
                },
            ) from exc

        orm = orm_result.scalar_one_or_none()

        if orm is None:
            return None

        return AssignmentMapper.to_domain(orm=orm)

    async def get_page(self, pagination: CursorPagination) -> Page[Assignment]:
        query = select(self.model)

        if pagination.cursor:
            query = query.where(self.model.id > pagination.cursor["id"])

        query = query.order_by(self.model.id).limit(pagination.limit + 1)

        try:
            orm_results = await self.session.execute(query)

        except SQLAlchemyError as exc:
            raise RepositoryInternalError(
                message="Failed to fetch Assignment page",
                details={
                    "entity": "assignment",
                    "operation": "get_page",
                    "limit": pagination.limit,
                    "cursor": pagination.cursor,
                },
            ) from exc

        orms = orm_results.scalars().all()
        has_next = len(orms) > pagination.limit

        if has_next:
            next_item = orms[pagination.limit]
            next_cursor = {"id": next_item.id}
        else:
            next_cursor = None

        return Page(
            items=[
                AssignmentMapper.to_domain(orm=orm) for orm in orms[: pagination.limit]
            ],
            next_cursor=next_cursor,
        )

    async def update(self, assignment: Assignment) -> Assignment:
        query = (
            update(self.model)
            .where(self.model.id == assignment.id)
            .values(
                title=assignment.title,
                description=assignment.description,
            )
            .returning(self.model)
        )

        try:
            orm_result = await self.session.execute(query)

        except IntegrityError as exc:
            raise RepositoryIntegrityError(
                message="Failed to update Assignment",
                details={
                    "entity": "assignment",
                    "operation": "update",
                    "id": assignment.id,
                    "title": assignment.title,
                    "description": assignment.description,
                },
            ) from exc

        except SQLAlchemyError as exc:
            raise RepositoryInternalError(
                message="Failed to update Assignment",
                details={
                    "entity": "assignment",
                    "operation": "update",
                    "id": assignment.id,
                    "title": assignment.title,
                    "description": assignment.description,
                },
            ) from exc

        orm = orm_result.scalar_one_or_none()

        if orm is None:
            raise RepositoryIntegrityError(
                message="Assignment not found",
                details={
                    "entity": "assignment",
                    "operation": "update",
                    "id": assignment.id,
                },
            )

        return AssignmentMapper.to_domain(orm=orm)

    async def delete(self, id: UUID) -> Assignment | None:
        query = delete(self.model).where(self.model.id == id).returning(self.model)

        try:
            orm_result = await self.session.execute(query)

        except SQLAlchemyError as exc:
            raise RepositoryInternalError(
                message="Failed to delete Assignment",
                details={
                    "entity": "assignment",
                    "operation": "delete",
                    "id": id,
                },
            ) from exc

        orm = orm_result.scalar_one_or_none()

        if orm is None:
            return None

        return AssignmentMapper.to_domain(orm=orm)
