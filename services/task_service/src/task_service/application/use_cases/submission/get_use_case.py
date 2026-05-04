from uuid import UUID

from task_service.domain.errors import DomainError
from task_service.application.dto.submission import SubmissionDTO
from task_service.application.dto.mappers import SubmissionMapper
from task_service.application.ports import UnitOfWork
from task_service.application.errors import (
    ApplicationError,
    NotFoundError,
    InternalError,
    ValidationError,
)


class GetSubmissionUseCase:
    def __init__(self, uow: UnitOfWork) -> None:
        self.uow = uow

    async def execute(self, id: UUID) -> SubmissionDTO:
        try:
            async with self.uow as uow:
                domain_result = await uow.submission_repo.get(id=id)

            if domain_result is None:
                raise NotFoundError(
                    message="Submission not found",
                    details={
                        "entity": "submission",
                        "id": id,
                    },
                )

            return SubmissionMapper.to_dto(domain=domain_result)

        except DomainError as exc:
            raise ValidationError(
                message=exc.message,
                details=exc.details,
            ) from exc

        except ApplicationError:
            raise

        except Exception as exc:
            raise InternalError(
                message="Failed to get Submission",
                details={
                    "entity": "submission",
                    "id": id,
                },
            ) from exc
