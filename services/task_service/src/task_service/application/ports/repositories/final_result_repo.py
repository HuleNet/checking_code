from uuid import UUID
from typing import Protocol

from task_service.domain.entities import FinalResult
from task_service.application.models.pagination import CursorPagination, Page


class FinalResultRepository(Protocol):
    async def add_many(self, final_results: list[FinalResult]) -> None: ...

    async def get(self, id: UUID) -> FinalResult | None: ...

    async def get_by_student_and_group_assignment(
        self, student_id: UUID, group_assignment_id: UUID
    ) -> FinalResult | None: ...

    async def get_by_group_assignment(
        self, group_assignment_id: UUID
    ) -> list[FinalResult]: ...

    async def get_page(
        self, group_assignment_id: UUID, pagination: CursorPagination
    ) -> Page[FinalResult]: ...

    async def delete(self, id: UUID) -> FinalResult | None: ...
