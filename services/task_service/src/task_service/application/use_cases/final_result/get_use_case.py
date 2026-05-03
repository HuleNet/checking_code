from uuid import UUID

from task_service.application.dto.final_result import FinalResultDTO
from task_service.application.dto.mappers import FinalResultMapper
from task_service.application.ports import UnitOfWork
from task_service.application.errors import (
    ApplicationError,
    NotFoundError,
    InternalError,
)


class GetFinalResultUseCase:
    def __init__(self, uow: UnitOfWork) -> None:
        self.uow = uow

    async def execute(self, id: UUID) -> FinalResultDTO:
        try:
            async with self.uow as uow:
                domain_result = await uow.final_result_repo.get(id=id)

            if domain_result is None:
                raise NotFoundError(
                    message="FinalResult not found",
                    details={
                        "entity": "final_result",
                        "id": id,
                    },
                )

            return FinalResultMapper.to_dto(domain=domain_result)

        except ApplicationError:
            raise

        except Exception as exc:
            raise InternalError(
                message="Failed to get FinalResult",
                details={
                    "entity": "final_result",
                    "id": id,
                },
            ) from exc
