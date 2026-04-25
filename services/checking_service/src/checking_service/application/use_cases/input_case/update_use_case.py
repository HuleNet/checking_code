from uuid import UUID

from checking_service.application.dto.input_case import InputCaseDTO, UpdateInputCaseDTO
from checking_service.application.dto.mappers import InputCaseMapper
from checking_service.application.ports import UnitOfWork
from checking_service.application.errors import (
    ApplicationError,
    NotFoundError,
    InternalError,
)


class UpdateInputCaseUseCase:
    def __init__(self, uow: UnitOfWork) -> None:
        self.uow = uow

    async def execute(self, id: UUID, dto: UpdateInputCaseDTO) -> InputCaseDTO:
        try:
            async with self.uow as uow:
                domain = await uow.input_case_repo.get(id=id)

            if domain is None:
                raise NotFoundError(
                    message="InputCase not found",
                    details={
                        "entity": "input_case",
                        "id": id,
                    },
                )

            updating_domain = InputCaseMapper.apply_update(
                domain=domain, update_dto=dto
            )
            result_domain = await uow.input_case_repo.update(input_case=updating_domain)
            await uow.commit()
            return InputCaseMapper.to_dto(domain=result_domain)

        except ApplicationError:
            raise

        except Exception as exc:
            raise InternalError(
                message="Failed to update InputCase",
                details={
                    "entity": "input_case",
                    "id": id,
                },
            ) from exc
