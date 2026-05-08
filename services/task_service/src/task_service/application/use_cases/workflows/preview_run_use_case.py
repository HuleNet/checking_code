from task_service.application.dto.evaluation import PreviewRunDTO, PreviewRunResultDTO
from task_service.application.ports import CheckingService


class PreviewRunUseCase:
    def __init__(self, checking_service: CheckingService) -> None:
        self.checking_service = checking_service

    async def execute(self, dto: PreviewRunDTO) -> PreviewRunResultDTO:
        return await self.checking_service.preview_run(dto=dto)
