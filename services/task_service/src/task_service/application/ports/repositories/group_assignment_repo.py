from uuid import UUID
from datetime import datetime
from typing import Protocol

from task_service.domain.entities import GroupAssignment
from task_service.application.models.pagination import CursorPagination, Page


class GroupAssignmentRepository(Protocol):
    async def add(self, group_assignment: GroupAssignment) -> GroupAssignment: ...

    async def get(self, id: UUID) -> GroupAssignment | None: ...

    async def get_by_group(self, group_id: UUID) -> list[GroupAssignment]: ...

    async def get_page(
        self, group_id: UUID, pagination: CursorPagination
    ) -> Page[GroupAssignment]: ...

    async def claim_expired(
        self, now: datetime, limit: int
    ) -> list[GroupAssignment]: ...

    async def reset_finalization(self, id: UUID) -> None: ...

    async def delete(self, id: UUID) -> GroupAssignment | None: ...
