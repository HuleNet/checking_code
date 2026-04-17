from uuid import UUID

from checking_service.application.dto.input_case import InputCaseDTO, UpdateInputCaseDTO
from checking_service.application.mappers import InputCaseMapper
from checking_service.application.ports import UnitOfWork
from checking_service.application.errors import NotFoundError


class UpdateInputCaseUseCase:
    def __init__(self, uow: UnitOfWork) -> None:
        self.uow = uow

    async def execute(self, id: UUID, dto: UpdateInputCaseDTO) -> InputCaseDTO:
        async with self.uow as uow:
            domain = await uow.input_case_repo.get(id=id)

        if domain is None:
            raise NotFoundError(
                message="InputCase not found",
                details={
                    "id": id,
                },
            )

        updating_domain = InputCaseMapper.apply_update(domain=domain, update_dto=dto)

        async with self.uow as uow:
            result_domain = await uow.input_case_repo.update(input_case=updating_domain)

        return InputCaseMapper.to_dto(domain=result_domain)
