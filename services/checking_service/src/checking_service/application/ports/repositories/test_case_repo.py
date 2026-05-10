from uuid import UUID
from typing import Protocol

from checking_service.domain.entities import TestCase
from checking_service.application.models.pagination import CursorPagination, Page


class TestCaseRepository(Protocol):
    async def add(self, test_case: TestCase) -> TestCase: ...

    async def get(self, id: UUID) -> TestCase | None: ...

    async def get_by_assignment(self, assignment_id: UUID) -> list[TestCase]: ...

    async def get_page(
        self, assignment_id: UUID, pagination: CursorPagination
    ) -> Page[TestCase]: ...

    async def update(self, test_case: TestCase) -> TestCase: ...

    async def delete(self, id: UUID) -> TestCase | None: ...
