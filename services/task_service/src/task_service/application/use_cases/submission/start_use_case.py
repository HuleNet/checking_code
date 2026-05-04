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


class StartSubmissionProcessingUseCase:
    def __init__(self, uow: UnitOfWork) -> None:
        self.uow = uow

    async def execute(self, id: UUID) -> SubmissionDTO:
        try:
            async with self.uow as uow:
                submission = await uow.submission_repo.get(id=id)

                if submission is None:
                    raise NotFoundError(
                        message="Submission not found",
                        details={
                            "entity": "submission",
                            "id": id,
                        },
                    )

                submission.start_processing()
                domain_result = await uow.submission_repo.update(submission=submission)
                await uow.track(entity=domain_result)
                await uow.commit()

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
                message="Failed to start Submission processing",
                details={
                    "entity": "submission",
                    "id": id,
                },
            ) from exc
