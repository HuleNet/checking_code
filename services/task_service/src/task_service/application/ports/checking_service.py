from typing import Protocol
from uuid import UUID

from task_service.application.dto.checking import CheckingResultDTO, PreviewRunDTO


class CheckingService(Protocol):
    async def evaluate_submission(
        self, submission_id: UUID, assignment_id: UUID, language: str, code: str
    ) -> CheckingResultDTO: ...
    async def preview_run(self, dto: PreviewRunDTO) -> CheckingResultDTO: ...
