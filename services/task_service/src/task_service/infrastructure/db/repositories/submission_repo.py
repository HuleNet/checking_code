from uuid import UUID

from sqlalchemy import insert, select, update, delete, func
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from task_service.domain.entities import Submission
from task_service.application.models.pagination import CursorPagination, Page
from task_service.application.ports.repositories import SubmissionRepository
from task_service.infrastructure.db.models import SubmissionORM
from task_service.infrastructure.db.models.mappers import SubmissionMapper
from task_service.infrastructure.errors import (
    RepositoryIntegrityError,
    RepositoryInternalError,
)


def _extract_constraint_name(exc: IntegrityError) -> str | None:
    orig = getattr(exc, "orig", None)
    diag = getattr(orig, "diag", None)

    if diag is None:
        return None

    return getattr(diag, "constraint_name", None)


class SQLAlchemySubmissionRepository(SubmissionRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.model = SubmissionORM

    async def add(self, submission: Submission) -> Submission:
        query = (
            insert(self.model)
            .values(**SubmissionMapper.to_dict(domain=submission))
            .returning(self.model)
        )

        try:
            orm_result = await self.session.execute(query)

        except IntegrityError as exc:
            constraint = _extract_constraint_name(exc=exc)

            if constraint == "uq_submission_student_code_hash":
                raise RepositoryIntegrityError(
                    message="Submission with this code already exists",
                    details={
                        "entity": "submission",
                        "operation": "add",
                        "constraint": constraint,
                        "student_id": submission.student_id,
                        "code_hash": submission.code_hash,
                    },
                ) from exc

            if constraint == "uq_submission_attempt":
                raise RepositoryIntegrityError(
                    message="Submission attempt collision",
                    details={
                        "entity": "submission",
                        "operation": "add",
                        "constraint": constraint,
                        "student_id": submission.student_id,
                        "group_assignment_id": submission.group_assignment_id,
                        "attempt_number": submission.attempt_number,
                    },
                ) from exc

            raise RepositoryIntegrityError(
                message="Submission already exists",
                details={
                    "entity": "submission",
                    "operation": "add",
                    "id": submission.id,
                },
            ) from exc

        except SQLAlchemyError as exc:
            raise RepositoryInternalError(
                message="Failed to insert Submission",
                details={
                    "entity": "submission",
                    "operation": "add",
                    "id": submission.id,
                },
            ) from exc

        orm = orm_result.scalar_one()
        return SubmissionMapper.to_domain(orm=orm)

    async def get_attempt_number_and_check(
        self,
        student_id: UUID,
        group_assignment_id: UUID,
        code_hash: str,
        max_attempts: int,
    ) -> int | None:
        duplicate_query = select(self.model.id).where(
            self.model.student_id == student_id,
            self.model.group_assignment_id == group_assignment_id,
            self.model.code_hash == code_hash,
        )
        attempts_query = select(func.count(self.model.id)).where(
            self.model.student_id == student_id,
            self.model.group_assignment_id == group_assignment_id,
        )

        try:
            duplicate_result = await self.session.execute(duplicate_query)
            duplicate_exists = duplicate_result.scalar_one_or_none()

            if duplicate_exists is not None:
                return None

            attempts_result = await self.session.execute(attempts_query)
            attempts_count = attempts_result.scalar_one()

        except SQLAlchemyError as exc:
            raise RepositoryInternalError(
                message="Failed to fetch attempt and check Submission",
                details={
                    "entity": "submission",
                    "operation": "get_attempt_number_and_check",
                    "student_id": student_id,
                },
            ) from exc

        next_attempt = attempts_count + 1

        if next_attempt > max_attempts:
            return 0

        return next_attempt

    async def get(self, id: UUID) -> Submission | None:
        query = select(self.model).where(self.model.id == id)

        try:
            orm_result = await self.session.execute(query)

        except SQLAlchemyError as exc:
            raise RepositoryInternalError(
                message="Failed to fetch Submission",
                details={
                    "entity": "submission",
                    "operation": "get",
                    "id": id,
                },
            ) from exc

        orm = orm_result.scalar_one_or_none()

        if orm is None:
            return None

        return SubmissionMapper.to_domain(orm=orm)

    async def get_by_group_assignment(
        self, group_assignment_id: UUID
    ) -> list[Submission]:
        query = select(self.model).where(
            self.model.group_assignment_id == group_assignment_id
        )

        try:
            orm_results = await self.session.execute(query)

        except SQLAlchemyError as exc:
            raise RepositoryInternalError(
                message="Failed to fetch Submissions by group_assignment",
                details={
                    "entity": "submission",
                    "operation": "get_by_group_assignment",
                    "group_assignment_id": group_assignment_id,
                },
            ) from exc

        return [
            SubmissionMapper.to_domain(orm=orm) for orm in orm_results.scalars().all()
        ]

    async def get_page(
        self, group_assignment_id: UUID, pagination: CursorPagination
    ) -> Page[Submission]:
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
                message="Failed to fetch Submission page",
                details={
                    "entity": "submission",
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
                SubmissionMapper.to_domain(orm=orm) for orm in orms[: pagination.limit]
            ],
            next_cursor=next_cursor,
        )

    async def update(self, submission: Submission) -> Submission:
        query = (
            update(self.model)
            .where(self.model.id == submission.id)
            .values(
                status=submission.status,
                tests_total=submission.tests_total,
                tests_passed=submission.tests_passed,
                evaluation_status=submission.evaluation_status,
                checked_at=submission.checked_at,
            )
            .returning(self.model)
        )

        try:
            orm_result = await self.session.execute(query)

        except IntegrityError as exc:
            raise RepositoryIntegrityError(
                message="Failed to update Submission",
                details={
                    "entity": "submission",
                    "operation": "update",
                    "id": submission.id,
                    "status": submission.status.value,
                    "tests_total": submission.tests_total,
                    "tests_passed": submission.tests_passed,
                    "checked_at": submission.checked_at,
                },
            ) from exc

        except SQLAlchemyError as exc:
            raise RepositoryInternalError(
                message="Failed to update Submission",
                details={
                    "entity": "submission",
                    "operation": "update",
                    "id": submission.id,
                    "status": submission.status.value,
                    "tests_total": submission.tests_total,
                    "tests_passed": submission.tests_passed,
                    "checked_at": submission.checked_at,
                },
            ) from exc

        orm = orm_result.scalar_one_or_none()

        if orm is None:
            raise RepositoryIntegrityError(
                message="Submission not found",
                details={
                    "entity": "submission",
                    "operation": "update",
                    "id": submission.id,
                },
            )

        return SubmissionMapper.to_domain(orm=orm)

    async def delete(self, id: UUID) -> Submission | None:
        query = delete(self.model).where(self.model.id == id).returning(self.model)

        try:
            orm_result = await self.session.execute(query)

        except SQLAlchemyError as exc:
            raise RepositoryInternalError(
                message="Failed to delete Submission",
                details={
                    "entity": "submission",
                    "operation": "delete",
                    "id": id,
                },
            ) from exc

        orm = orm_result.scalar_one_or_none()

        if orm is None:
            return None

        return SubmissionMapper.to_domain(orm=orm)
