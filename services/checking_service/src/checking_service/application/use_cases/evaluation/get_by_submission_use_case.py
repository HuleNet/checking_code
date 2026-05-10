from uuid import UUID

from checking_service.domain.errors import DomainError
from checking_service.application.dto.evaluation import EvaluationDTO
from checking_service.application.dto.mappers import EvaluationMapper
from checking_service.application.ports import UnitOfWork
from checking_service.application.errors import (
    ApplicationError,
    InternalError,
    ValidationError,
)


class GetEvaluationsBySubmissionUseCase:
    def __init__(self, uow: UnitOfWork) -> None:
        self.uow = uow

    async def execute(self, submission_id: UUID) -> list[EvaluationDTO]:
        try:
            async with self.uow as uow:
                domain_results = await uow.evaluation_repo.get_by_submission(
                    submission_id=submission_id
                )

            return [EvaluationMapper.to_dto(domain=domain) for domain in domain_results]

        except DomainError as exc:
            raise ValidationError(
                message=exc.message,
                details=exc.details,
            ) from exc

        except ApplicationError:
            raise

        except Exception as exc:
            raise InternalError(
                message="Failed to get Evaluations",
                details={
                    "entity": "evaluation",
                    "submission_id": submission_id,
                    "is_page": False,
                },
            ) from exc
