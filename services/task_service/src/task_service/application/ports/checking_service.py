from typing import Protocol
from uuid import UUID

from task_service.application.dto.evaluation import (
    EvaluationDTO,
    PreviewRunDTO,
    PreviewRunResultDTO,
)


class CheckingService(Protocol):
    async def start_evaluation(
        self, submission_id: UUID, assignment_id: UUID, language: str, code: str
    ) -> EvaluationDTO: ...
    async def get_evaluation(self, evaluation_id: str) -> EvaluationDTO: ...
    async def preview_run(self, dto: PreviewRunDTO) -> PreviewRunResultDTO: ...
