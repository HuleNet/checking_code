from uuid import uuid4

from checking_service.application.dto.input_case import CreateInputCaseDTO, InputCaseDTO
from checking_service.application.dto.mappers import InputCaseMapper
from checking_service.application.ports import UnitOfWork
from checking_service.application.errors import ApplicationError, InternalError


class CreateInputCaseUseCase:
    def __init__(
        self,
        uow: UnitOfWork,
    ) -> None:
        self.uow = uow

    async def execute(self, dto: CreateInputCaseDTO) -> InputCaseDTO:
        try:
            async with self.uow as uow:
                input_case = InputCaseMapper.to_domain(dto=dto, id=uuid4())
                domain_result = await uow.input_case_repo.add(input_case=input_case)
                await uow.commit()

            return InputCaseMapper.to_dto(domain=domain_result)

        except ApplicationError:
            raise

        except Exception as exc:
            raise InternalError(
                message="Failed to create InputCase",
                details={
                    "entity": "input_case",
                },
            ) from exc
