from uuid import UUID
from typing import Protocol

from task_service.domain.entities import Assignment
from task_service.application.models.pagination import CursorPagination, Page


class AssignmentRepository(Protocol):
    async def add(self, assignment: Assignment) -> Assignment: ...

    async def get(self, id: UUID) -> Assignment | None: ...

    async def get_page(self, pagination: CursorPagination) -> Page[Assignment]: ...

    async def update(self, assignment: Assignment) -> Assignment: ...

    async def delete(self, id: UUID) -> Assignment | None: ...
