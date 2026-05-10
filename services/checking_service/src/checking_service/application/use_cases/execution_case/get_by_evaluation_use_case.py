from uuid import UUID

from checking_service.domain.errors import DomainError
from checking_service.application.dto.execution_case import ExecutionCaseDTO
from checking_service.application.dto.mappers import ExecutionCaseMapper
from checking_service.application.ports import UnitOfWork
from checking_service.application.errors import (
    ApplicationError,
    InternalError,
    ValidationError,
)


class GetExecutionCasesByEvaluationUseCase:
    def __init__(self, uow: UnitOfWork) -> None:
        self.uow = uow

    async def execute(self, evaluation_id: UUID) -> list[ExecutionCaseDTO]:
        try:
            async with self.uow as uow:
                domain_results = await uow.execution_case_repo.get_by_evaluation(
                    evaluation_id=evaluation_id
                )

            return [
                ExecutionCaseMapper.to_dto(domain=domain) for domain in domain_results
            ]

        except DomainError as exc:
            raise ValidationError(
                message=exc.message,
                details=exc.details,
            ) from exc

        except ApplicationError:
            raise

        except Exception as exc:
            raise InternalError(
                message="Failed to get ExecutionCases",
                details={
                    "entity": "execution_case",
                    "evaluation_id": evaluation_id,
                    "is_page": False,
                },
            ) from exc
