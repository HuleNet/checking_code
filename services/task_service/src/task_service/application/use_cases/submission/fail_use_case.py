from uuid import UUID

from task_service.domain.value_objects import SubmissionStatus
from task_service.domain.errors import DomainError
from task_service.application.ports import UnitOfWork
from task_service.application.errors import (
    ApplicationError,
    NotFoundError,
    InternalError,
    ValidationError,
)


class FailSubmissionUseCase:
    def __init__(self, uow: UnitOfWork) -> None:
        self.uow = uow

    async def execute(self, id: UUID) -> None:
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

                if submission.status != SubmissionStatus.PENDING:
                    return

                submission.fail()
                await uow.submission_repo.update(submission=submission)
                await uow.commit()

        except DomainError as exc:
            raise ValidationError(
                message=exc.message,
                details=exc.details,
            ) from exc

        except ApplicationError:
            raise

        except Exception as exc:
            raise InternalError(
                message="Failed to mark Submission as failed",
                details={
                    "entity": "submission",
                    "id": id,
                },
            ) from exc
