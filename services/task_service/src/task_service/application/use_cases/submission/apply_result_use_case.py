from task_service.domain.errors import DomainError
from task_service.application.dto.submission import (
    SubmissionDTO,
    ApplySubmissionResultDTO,
)
from task_service.application.dto.mappers import SubmissionMapper
from task_service.application.ports import UnitOfWork
from task_service.application.errors import (
    ApplicationError,
    NotFoundError,
    InternalError,
    ValidationError,
)


class ApplySubmissionResultUseCase:
    def __init__(self, uow: UnitOfWork) -> None:
        self.uow = uow

    async def execute(self, dto: ApplySubmissionResultDTO) -> SubmissionDTO:
        try:
            async with self.uow as uow:
                submission = await uow.submission_repo.get(id=dto.id)

                if submission is None:
                    raise NotFoundError(
                        message="Submission not found",
                        details={
                            "entity": "submission",
                            "id": dto.id,
                        },
                    )

                submission.apply_result(
                    tests_passed=dto.tests_passed, tests_total=dto.tests_total
                )
                result_domain = await uow.submission_repo.update(submission=submission)
                await uow.track(entity=result_domain)
                await uow.commit()

            return SubmissionMapper.to_dto(domain=result_domain)

        except DomainError as exc:
            raise ValidationError(
                message=exc.message,
                details=exc.details,
            ) from exc

        except ApplicationError:
            raise

        except Exception as exc:
            raise InternalError(
                message="Failed to apply Submission result",
                details={
                    "entity": "submission",
                    "id": dto.id,
                },
            ) from exc
