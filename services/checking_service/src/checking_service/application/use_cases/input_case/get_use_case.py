from uuid import UUID

from checking_service.application.dto.input_case import InputCaseDTO
from checking_service.application.dto.mappers import InputCaseMapper
from checking_service.application.ports import UnitOfWork
from checking_service.application.errors import (
    ApplicationError,
    NotFoundError,
    InternalError,
)


class GetInputCaseUseCase:
    def __init__(self, uow: UnitOfWork) -> None:
        self.uow = uow

    async def execute(self, id: UUID) -> InputCaseDTO:
        try:
            async with self.uow as uow:
                domain_result = await uow.input_case_repo.get(id=id)

            if domain_result is None:
                raise NotFoundError(
                    message="InputCase not found",
                    details={
                        "entity": "input_case",
                        "id": id,
                    },
                )

            return InputCaseMapper.to_dto(domain=domain_result)

        except ApplicationError:
            raise

        except Exception as exc:
            raise InternalError(
                message="Failed to get InputCase",
                details={
                    "entity": "input_case",
                    "id": id,
                },
            ) from exc
