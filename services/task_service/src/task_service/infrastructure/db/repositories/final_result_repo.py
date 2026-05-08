from uuid import UUID

from sqlalchemy import select, delete
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import insert

from task_service.domain.entities import FinalResult
from task_service.application.models.pagination import CursorPagination, Page
from task_service.application.ports.repositories import FinalResultRepository
from task_service.infrastructure.db.models import FinalResultORM
from task_service.infrastructure.db.models.mappers import FinalResultMapper
from task_service.infrastructure.errors import (
    RepositoryIntegrityError,
    RepositoryInternalError,
)


class SQLAlchemyFinalResultRepository(FinalResultRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.model = FinalResultORM

    async def add_many(self, final_results: list[FinalResult]) -> None:
        if not final_results:
            return

        values = [
            FinalResultMapper.to_dict(domain=final_result)
            for final_result in final_results
        ]
        query = insert(self.model).values(values)
        query = query.on_conflict_do_update(
            constraint="uq_final_result_group_assignment_student",
            set_={
                "submission_id": query.excluded.submission_id,
                "score": query.excluded.score,
                "attempt_number": query.excluded.attempt_number,
                "tests_total": query.excluded.tests_total,
                "tests_passed": query.excluded.tests_passed,
                "plagiarism_score": query.excluded.plagiarism_score,
                "plagiarism_flag": query.excluded.plagiarism_flag,
                "finalized_at": query.excluded.finalized_at,
            },
        )

        try:
            await self.session.execute(query)

        except IntegrityError as exc:
            raise RepositoryIntegrityError(
                message="Failed to upsert FinalResults",
                details={
                    "entity": "final_result",
                    "operation": "add_many",
                    "final_results_count": len(final_results),
                },
            ) from exc

        except SQLAlchemyError as exc:
            raise RepositoryInternalError(
                message="Failed to bulk insert FinalResults",
                details={
                    "entity": "final_result",
                    "operation": "add_many",
                    "final_results_count": len(final_results),
                },
            ) from exc

    async def get(self, id: UUID) -> FinalResult | None:
        query = select(self.model).where(self.model.id == id)

        try:
            orm_result = await self.session.execute(query)

        except SQLAlchemyError as exc:
            raise RepositoryInternalError(
                message="Failed to fetch FinalResult",
                details={
                    "entity": "final_result",
                    "operation": "get",
                    "id": id,
                },
            ) from exc

        orm = orm_result.scalar_one_or_none()

        if orm is None:
            return None

        return FinalResultMapper.to_domain(orm=orm)

    async def get_by_group_assignment(
        self, group_assignment_id: UUID
    ) -> list[FinalResult]:
        query = select(self.model).where(
            self.model.group_assignment_id == group_assignment_id
        )

        try:
            orm_results = await self.session.execute(query)

        except SQLAlchemyError as exc:
            raise RepositoryInternalError(
                message="Failed to fetch FinalResults by group_assignment",
                details={
                    "entity": "group_assignment",
                    "operation": "get_by_group_assignment",
                    "group_assignment_id": group_assignment_id,
                },
            ) from exc

        return [
            FinalResultMapper.to_domain(orm=orm) for orm in orm_results.scalars().all()
        ]

    async def get_page(
        self, group_assignment_id: UUID, pagination: CursorPagination
    ) -> Page[FinalResult]:
        query = select(self.model).where(
            self.model.group_assignment_id == group_assignment_id
        )

        if pagination.cursor:
            query = query.where(self.model.id > pagination.cursor["id"])

        query = query.order_by(self.model.id).limit(pagination.limit + 1)

        try:
            orm_results = await self.session.execute(query)

        except SQLAlchemyError as exc:
            raise RepositoryInternalError(
                message="Failed to fetch FinalResult page",
                details={
                    "entity": "group_assignment",
                    "operation": "get_page",
                    "group_assignment_id": group_assignment_id,
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
                FinalResultMapper.to_domain(orm=orm) for orm in orms[: pagination.limit]
            ],
            next_cursor=next_cursor,
        )

    async def delete(self, id: UUID) -> FinalResult | None:
        query = delete(self.model).where(self.model.id == id).returning(self.model)

        try:
            orm_result = await self.session.execute(query)

        except SQLAlchemyError as exc:
            raise RepositoryInternalError(
                message="Failed to delete FinalResult",
                details={
                    "entity": "final_result",
                    "operation": "delete",
                    "id": id,
                },
            ) from exc

        orm = orm_result.scalar_one_or_none()

        if orm is None:
            return None

        return FinalResultMapper.to_domain(orm=orm)
