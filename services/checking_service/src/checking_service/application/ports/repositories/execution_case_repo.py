from uuid import UUID
from typing import Protocol

from checking_service.domain.entities import ExecutionCase
from checking_service.application.pagination import CursorPagination, Page


class ExecutionCaseRepository(Protocol):
    async def add(self, execution_case: ExecutionCase) -> ExecutionCase: ...

    async def get(self, id: UUID) -> ExecutionCase | None: ...

    async def get_by_evaluation(
        self, evaluation_id: UUID, pagination: CursorPagination
    ) -> Page[ExecutionCase]: ...

    async def delete(self, id: UUID) -> ExecutionCase | None: ...
