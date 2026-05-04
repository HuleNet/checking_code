from uuid import UUID

from task_service.domain.errors import DomainError
from task_service.application.dto.final_result import FinalResultDTO
from task_service.application.dto.mappers import FinalResultMapper
from task_service.application.ports import UnitOfWork
from task_service.application.errors import (
    ApplicationError,
    NotFoundError,
    InternalError,
    ValidationError,
)


class DeleteFinalResultUseCase:
    def __init__(self, uow: UnitOfWork) -> None:
        self.uow = uow

    async def execute(self, id: UUID) -> FinalResultDTO:
        try:
            async with self.uow as uow:
                domain_result = await uow.final_result_repo.delete(id=id)

                if domain_result is None:
                    raise NotFoundError(
                        message="FinalResult not found",
                        details={
                            "entity": "final_result",
                            "id": id,
                        },
                    )

                await uow.commit()

            return FinalResultMapper.to_dto(domain=domain_result)

        except DomainError as exc:
            raise ValidationError(
                message=exc.message,
                details=exc.details,
            ) from exc

        except ApplicationError:
            raise

        except Exception as exc:
            raise InternalError(
                message="Failed to delete FinalResult",
                details={
                    "entity": "final_result",
                    "id": id,
                },
            ) from exc
