from uuid import UUID
from typing import Protocol

from checking_service.domain.entities import Evaluation
from checking_service.application.models.pagination import CursorPagination, Page


class EvaluationRepository(Protocol):
    async def add(self, evaluation: Evaluation) -> Evaluation: ...

    async def get(self, id: UUID) -> Evaluation | None: ...

    async def get_by_submission(self, submission_id: UUID) -> list[Evaluation]: ...

    async def get_page(
        self, submission_id: UUID, pagination: CursorPagination
    ) -> Page[Evaluation]: ...

    async def claim_for_run(
        self, id: UUID, stuck_timeout_sec: int
    ) -> Evaluation | None: ...

    async def update(self, evaluation: Evaluation) -> Evaluation: ...

    async def delete(self, id: UUID) -> Evaluation | None: ...
