from uuid import UUID

from checking_service.domain.errors import DomainError
from checking_service.application.dto.evaluation import EvaluationDTO
from checking_service.application.dto.mappers import EvaluationMapper
from checking_service.application.ports import UnitOfWork
from checking_service.application.errors import (
    ApplicationError,
    NotFoundError,
    InternalError,
    ValidationError,
)


class DeleteEvaluationUseCase:
    def __init__(self, uow: UnitOfWork) -> None:
        self.uow = uow

    async def execute(self, id: UUID) -> EvaluationDTO:
        try:
            async with self.uow as uow:
                domain_result = await uow.evaluation_repo.delete(id=id)

                if domain_result is None:
                    raise NotFoundError(
                        message="Evaluation not found",
                        details={
                            "entity": "evaluation",
                            "id": id,
                        },
                    )

                await uow.commit()

            return EvaluationMapper.to_dto(domain=domain_result)

        except DomainError as exc:
            raise ValidationError(
                message=exc.message,
                details=exc.details,
            ) from exc

        except ApplicationError:
            raise

        except Exception as exc:
            raise InternalError(
                message="Failed to delete Evaluation",
                details={
                    "entity": "evaluation",
                    "id": id,
                },
            ) from exc
