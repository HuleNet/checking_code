from uuid import UUID
from datetime import datetime, timezone

from sqlalchemy import insert, select, update, delete
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from task_service.domain.value_objects import GroupAssignmentStatus
from task_service.domain.entities import GroupAssignment
from task_service.application.models.pagination import CursorPagination, Page
from task_service.application.ports.repositories import GroupAssignmentRepository
from task_service.infrastructure.db.models import GroupAssignmentORM
from task_service.infrastructure.db.models.mappers import GroupAssignmentMapper
from task_service.infrastructure.errors import (
    RepositoryIntegrityError,
    RepositoryInternalError,
)


class SQLAlchemyGroupAssignmentRepository(GroupAssignmentRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.model = GroupAssignmentORM

    async def add(self, group_assignment: GroupAssignment) -> GroupAssignment:
        query = (
            insert(self.model)
            .values(**GroupAssignmentMapper.to_dict(domain=group_assignment))
            .returning(self.model)
        )

        try:
            orm_result = await self.session.execute(query)

        except IntegrityError as exc:
            raise RepositoryIntegrityError(
                message="GroupAssignment already exists",
                details={
                    "entity": "group_assignment",
                    "operation": "add",
                    "id": group_assignment.id,
                },
            ) from exc

        except SQLAlchemyError as exc:
            raise RepositoryInternalError(
                message="Failed to insert GroupAssignment",
                details={
                    "entity": "group_assignment",
                    "operation": "add",
                    "id": group_assignment.id,
                },
            ) from exc

        orm = orm_result.scalar_one()
        return GroupAssignmentMapper.to_domain(orm=orm)

    async def get(self, id: UUID) -> GroupAssignment | None:
        query = select(self.model).where(self.model.id == id)

        try:
            orm_result = await self.session.execute(query)

        except SQLAlchemyError as exc:
            raise RepositoryInternalError(
                message="Failed to fetch GroupAssignment",
                details={
                    "entity": "group_assignment",
                    "operation": "get",
                    "id": id,
                },
            ) from exc

        orm = orm_result.scalar_one_or_none()

        if orm is None:
            return None

        return GroupAssignmentMapper.to_domain(orm=orm)

    async def get_by_group(self, group_id: UUID) -> list[GroupAssignment]:
        query = select(self.model).where(self.model.group_id == group_id)

        try:
            orm_results = await self.session.execute(query)

        except SQLAlchemyError as exc:
            raise RepositoryInternalError(
                message="Failed to fetch GroupAssignment by group",
                details={
                    "entity": "group_assignment",
                    "operation": "get_by_group",
                    "group_id": group_id,
                },
            ) from exc

        return [
            GroupAssignmentMapper.to_domain(orm=orm)
            for orm in orm_results.scalars().all()
        ]

    async def get_page(
        self, group_id: UUID, pagination: CursorPagination
    ) -> Page[GroupAssignment]:
        query = select(self.model).where(self.model.group_id == group_id)

        if pagination.cursor:
            query = query.where(self.model.id > pagination.cursor["id"])

        query = query.order_by(self.model.id).limit(pagination.limit + 1)

        try:
            orm_results = await self.session.execute(query)

        except SQLAlchemyError as exc:
            raise RepositoryInternalError(
                message="Failed to fetch GroupAssignment page",
                details={
                    "entity": "group_assignment",
                    "operation": "get_page",
                    "group_id": group_id,
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
                GroupAssignmentMapper.to_domain(orm=orm)
                for orm in orms[: pagination.limit]
            ],
            next_cursor=next_cursor,
        )

    async def claim_expired(self, now: datetime, limit: int) -> list[GroupAssignment]:
        subquery = (
            select(self.model)
            .where(
                self.model.deadline <= now,
                self.model.status == GroupAssignmentStatus.ACTIVE,
            )
            .with_for_update(skip_locked=True)
            .limit(limit)
        )
        query = (
            update(self.model)
            .where(self.model.id.in_(subquery))
            .values(
                status=GroupAssignmentStatus.FINALIZING,
            )
            .returning(self.model)
        )

        try:
            orm_results = await self.session.execute(query)

        except SQLAlchemyError as exc:
            raise RepositoryInternalError(
                message="Failed to claim expired GroupAssignments",
                details={
                    "entity": "group_assignment",
                    "operation": "claim_expired",
                    "limit": limit,
                },
            ) from exc

        orms = orm_results.scalars().all()

        return [GroupAssignmentMapper.to_domain(orm=orm) for orm in orms]

    async def finalize(self, id: UUID) -> None:
        query = (
            update(self.model)
            .where(
                self.model.id == id,
                self.model.status == GroupAssignmentStatus.FINALIZING,
            )
            .values(
                status=GroupAssignmentStatus.FINALIZED,
                finalized_at=datetime.now(timezone.utc),
            )
        )

        try:
            await self.session.execute(query)

        except SQLAlchemyError as exc:
            raise RepositoryInternalError(
                message="Failed to finalize GroupAssignment",
                details={
                    "entity": "group_assignment",
                    "operation": "finalize",
                    "id": id,
                },
            ) from exc

    async def reset_finalization(self, id: UUID) -> None:
        query = (
            update(self.model)
            .where(self.model.id == id)
            .values(
                status=GroupAssignmentStatus.ACTIVE,
            )
        )

        try:
            await self.session.execute(query)

        except SQLAlchemyError as exc:
            raise RepositoryInternalError(
                message="Failed to reset GroupAssignment finalization",
                details={
                    "entity": "reset_finalization",
                    "operation": "finalize",
                    "id": id,
                },
            ) from exc

    async def delete(self, id: UUID) -> GroupAssignment | None:
        query = delete(self.model).where(self.model.id == id).returning(self.model)

        try:
            orm_result = await self.session.execute(query)

        except SQLAlchemyError as exc:
            raise RepositoryInternalError(
                message="Failed to delete GroupAssignment",
                details={
                    "entity": "group_assignment",
                    "operation": "delete",
                    "id": id,
                },
            ) from exc

        orm = orm_result.scalar_one_or_none()

        if orm is None:
            return None

        return GroupAssignmentMapper.to_domain(orm=orm)
