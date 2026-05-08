from task_service.application.dto.checking import PreviewRunDTO, CheckingResultDTO
from task_service.application.ports import CheckingService


class PreviewRunUseCase:
    def __init__(self, checking_service: CheckingService) -> None:
        self.checking_service = checking_service

    async def execute(self, dto: PreviewRunDTO) -> CheckingResultDTO:
        return await self.checking_service.preview_run(dto=dto)
