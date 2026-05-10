from uuid import UUID

from checking_service.domain.errors import DomainError
from checking_service.application.dto.execution_case import ExecutionCaseDTO
from checking_service.application.dto.mappers import ExecutionCaseMapper
from checking_service.application.ports import UnitOfWork
from checking_service.application.errors import (
    ApplicationError,
    NotFoundError,
    InternalError,
    ValidationError,
)


class GetExecutionCaseUseCase:
    def __init__(self, uow: UnitOfWork) -> None:
        self.uow = uow

    async def execute(self, id: UUID) -> ExecutionCaseDTO:
        try:
            async with self.uow as uow:
                domain_result = await uow.execution_case_repo.get(id=id)

            if domain_result is None:
                raise NotFoundError(
                    message="ExecutionCase not found",
                    details={
                        "entity": "execution_case",
                        "id": id,
                    },
                )

            return ExecutionCaseMapper.to_dto(domain=domain_result)

        except DomainError as exc:
            raise ValidationError(
                message=exc.message,
                details=exc.details,
            ) from exc

        except ApplicationError:
            raise

        except Exception as exc:
            raise InternalError(
                message="Failed to get ExecutionCase",
                details={
                    "entity": "execution_case",
                    "id": id,
                },
            ) from exc
