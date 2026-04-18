from typing import Protocol
from uuid import UUID

from checking_service.domain.entities import ExecutionCase
from checking_service.application.models.pagination import CursorPagination, Page


class ExecutionCaseRepository(Protocol):
    async def add_many(
        self, execution_cases: list[ExecutionCase]
    ) -> list[ExecutionCase]: ...
    async def get(self, id: UUID) -> ExecutionCase | None: ...
    async def get_by_evaluation(self, evaluation_id: UUID) -> list[ExecutionCase]: ...
    async def get_page(
        self, evaluation_id: UUID, pagination: CursorPagination
    ) -> Page[ExecutionCase]: ...
    async def update_many(
        self, execution_cases: list[ExecutionCase]
    ) -> list[ExecutionCase]: ...
