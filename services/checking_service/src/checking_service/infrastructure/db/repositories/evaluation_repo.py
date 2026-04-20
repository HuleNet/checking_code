from uuid import UUID
from datetime import datetime, timezone, timedelta

from sqlalchemy import insert, select, update, delete, or_, and_
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from checking_service.domain.enums import EvaluationStatus
from checking_service.domain.entities import Evaluation
from checking_service.application.models.pagination import CursorPagination, Page
from checking_service.application.ports.repositories import EvaluationRepository
from checking_service.infrastructure.db.models import EvaluationORM
from checking_service.infrastructure.db.models.mappers import EvaluationMapper
from checking_service.infrastructure.errors import (
    RepositoryIntegrityError,
    InternalRepositoryError,
)


class SQLAlchemyEvaluationRepository(EvaluationRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.model = EvaluationORM

    async def add(self, evaluation: Evaluation) -> Evaluation:
        query = (
            insert(self.model)
            .values(**EvaluationMapper.to_dict(domain=evaluation))
            .returning(self.model)
        )

        try:
            orm_result = await self.session.execute(query)

        except IntegrityError as exc:
            raise RepositoryIntegrityError(
                message="Evaluation already exists",
                details={
                    "id": evaluation.id,
                },
            ) from exc

        except SQLAlchemyError as exc:
            raise InternalRepositoryError(
                message="Database error",
                details={},
            ) from exc

        orm = orm_result.scalar_one()
        return EvaluationMapper.to_domain(orm=orm)

    async def get(self, id: UUID) -> Evaluation | None:
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

        return EvaluationMapper.to_domain(orm=orm)

    async def get_by_submission(self, submission_id: UUID) -> list[Evaluation]:
        query = select(self.model).where(self.model.submission_id == submission_id)

        try:
            orm_results = await self.session.execute(query)

        except SQLAlchemyError as exc:
            raise InternalRepositoryError(
                message="Database error",
                details={},
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
            items=[EvaluationMapper.to_domain(orm=orm) for orm in orms],
            next_cursor=next_cursor,
        )

    async def claim_for_run(
        self, id: UUID, stuck_timeout_sec: int
    ) -> Evaluation | None:
        now = datetime.now(timezone.utc)
        stuck_border = now - timedelta(seconds=stuck_timeout_sec)
        query = (
            update(self.model)
            .where(
                self.model.id == id,
                or_(
                    self.model.status == EvaluationStatus.PENDING,
                    and_(
                        self.model.status == EvaluationStatus.RUNNING,
                        or_(
                            self.model.started_at < stuck_border,
                            self.model.started_at.is_(None),
                        ),
                    ),
                ),
            )
            .values(
                status=EvaluationStatus.RUNNING,
                started_at=now,
            )
            .returning(self.model)
        )

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

        return EvaluationMapper.to_domain(orm=orm)

    async def update(self, evaluation: Evaluation) -> Evaluation:
        query = (
            update(self.model)
            .where(
                self.model.id == evaluation.id,
                self.model.status == EvaluationStatus.RUNNING,
                self.model.started_at == evaluation.started_at,
            )
            .values(
                status=evaluation.status,
                passed_tests_count=evaluation.passed_tests_count,
            )
            .returning(self.model)
        )

        try:
            orm_result = await self.session.execute(query)

        except IntegrityError as exc:
            raise RepositoryIntegrityError(
                message="Update Evaluation failed",
                details={
                    "updated_status": evaluation.status.value,
                    "updated_passed_tests_count": evaluation.passed_tests_count,
                },
            ) from exc

        except SQLAlchemyError as exc:
            raise InternalRepositoryError(
                message="Database error",
                details={},
            ) from exc

        orm = orm_result.scalar_one_or_none()

        if orm is None:
            raise RepositoryIntegrityError(
                message="Evaluation not found or invalid state",
                details={
                    "id": evaluation.id,
                    "expected_started_at": evaluation.started_at,
                    "reason": "optimistic_lock_failed",
                },
            )

        return EvaluationMapper.to_domain(orm=orm)

    async def delete(self, id: UUID) -> Evaluation | None:
        query = delete(self.model).where(self.model.id == id).returning(self.model)

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

        return EvaluationMapper.to_domain(orm=orm)
