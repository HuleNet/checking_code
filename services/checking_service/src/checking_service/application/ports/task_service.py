from typing import Protocol

from checking_service.application.dto.evaluation import EvaluationDTO


class TaskService(Protocol):
    async def complete_submission(self, dto: EvaluationDTO) -> None: ...
