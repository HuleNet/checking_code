from uuid import uuid4

from checking_service.application.dto.input_case import CreateInputCaseDTO, InputCaseDTO
from checking_service.application.mappers import InputCaseMapper
from checking_service.application.ports import UnitOfWork


class CreateInputCaseUseCase:
    def __init__(
        self,
        uow: UnitOfWork,
    ) -> None:
        self.uow = uow

    async def execute(self, dto: CreateInputCaseDTO) -> InputCaseDTO:
        async with self.uow as uow:
            input_case = InputCaseMapper.to_domain(dto=dto, id=uuid4())
            domain_result = await uow.input_case_repo.add(input_case=input_case)
            await self.uow.commit()
            return InputCaseMapper.to_dto(domain=domain_result)
