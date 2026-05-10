from uuid import UUID
from typing import Protocol

from task_service.domain.entities import Submission
from task_service.application.models.pagination import CursorPagination, Page


class SubmissionRepository(Protocol):
    async def add(self, submission: Submission) -> Submission: ...

    async def get_attempt_number_and_check(
        self,
        student_id: UUID,
        group_assignment_id: UUID,
        code_hash: str,
        max_attempts: int,
    ) -> int | None: ...

    async def get(self, id: UUID) -> Submission | None: ...

    async def get_by_group_assignment(
        self, group_assignment_id: UUID
    ) -> list[Submission]: ...

    async def get_page(
        self, group_assignment_id: UUID, pagination: CursorPagination
    ) -> Page[Submission]: ...

    async def update(self, submission: Submission) -> Submission: ...

    async def delete(self, id: UUID) -> Submission | None: ...
