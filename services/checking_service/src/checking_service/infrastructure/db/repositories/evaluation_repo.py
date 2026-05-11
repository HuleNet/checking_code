from uuid import UUID

from sqlalchemy import insert, select, delete
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from checking_service.domain.entities import Evaluation
from checking_service.application.models.pagination import CursorPagination, Page
from checking_service.application.ports.repositories import EvaluationRepository
from checking_service.infrastructure.db.models import EvaluationORM
from checking_service.infrastructure.db.models.mappers import EvaluationMapper
from checking_service.infrastructure.errors import (
    RepositoryIntegrityError,
    RepositoryInternalError,
)


class SQLAlchemyEvaluationRepository(EvaluationRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.model = EvaluationORM

    async def add(self, evaluation: Evaluation) -> None:
        query = insert(self.model).values(**EvaluationMapper.to_dict(domain=evaluation))

        try:
            await self.session.execute(query)

        except IntegrityError as exc:
            raise RepositoryIntegrityError(
                message="Evaluation already exists",
                details={
                    "entity": "evaluation",
                    "operation": "add",
                    "id": evaluation.id,
                },
            ) from exc

        except SQLAlchemyError as exc:
            raise RepositoryInternalError(
                message="Failed to insert Evaluation",
                details={
                    "entity": "evaluation",
                    "operation": "add",
                    "id": evaluation.id,
                },
            ) from exc

    async def get(self, id: UUID) -> Evaluation | None:
        query = select(self.model).where(self.model.id == id)

        try:
            orm_result = await self.session.execute(query)

        except SQLAlchemyError as exc:
            raise RepositoryInternalError(
                message="Failed to fetch Evaluation",
                details={
                    "entity": "evaluation",
                    "operation": "get",
                    "id": id,
                },
            ) from exc

        orm = orm_result.scalar_one_or_none()

        if orm is None:
            return None

        return EvaluationMapper.to_domain(orm=orm)

    async def get_by_submission(self, submission_id: UUID) -> list[Evaluation]:
        query = select(self.model).where(self.model.submission_id == submission_id)

        try:
            orm_results = await self.session.execute(query)

        except SQLAlchemyError as exc:
            raise RepositoryInternalError(
                message="Failed to fetch Evaluations by submission",
                details={
                    "entity": "evaluation",
                    "operation": "get_by_submission",
                    "submission_id": submission_id,
                },
            ) from exc

        return [
            EvaluationMapper.to_domain(orm=orm) for orm in orm_results.scalars().all()
        ]

    async def get_page(
        self, submission_id: UUID, pagination: CursorPagination
    ) -> Page[Evaluation]:
        query = select(self.model).where(self.model.submission_id == submission_id)

        if pagination.cursor:
            query = query.where(self.model.id > pagination.cursor["id"])

        query = query.order_by(self.model.id).limit(pagination.limit + 1)

        try:
            orm_results = await self.session.execute(query)

        except SQLAlchemyError as exc:
            raise RepositoryInternalError(
                message="Failed to fetch Evaluation page",
                details={
                    "entity": "evaluation",
                    "operation": "get_page",
                    "submission_id": submission_id,
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
            items=[EvaluationMapper.to_domain(orm=orm) for orm in orms],
            next_cursor=next_cursor,
        )

    async def delete(self, id: UUID) -> Evaluation | None:
        query = delete(self.model).where(self.model.id == id).returning(self.model)

        try:
            orm_result = await self.session.execute(query)

        except SQLAlchemyError as exc:
            raise RepositoryInternalError(
                message="Failed to delete Evaluation",
                details={
                    "entity": "evaluation",
                    "operation": "delete",
                    "id": id,
                },
            ) from exc

        orm = orm_result.scalar_one_or_none()

        if orm is None:
            return None

        return EvaluationMapper.to_domain(orm=orm)
