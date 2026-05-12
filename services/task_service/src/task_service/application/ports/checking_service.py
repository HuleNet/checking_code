from uuid import UUID
from typing import Protocol


class CheckingService(Protocol):
    async def create_evaluation(
        self,
        submission_id: UUID,
        assignment_id: UUID,
        code: str,
        language: str,
    ) -> None: ...
