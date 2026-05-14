from typing import cast

from task_service.domain.value_objects import SubmissionStatus, EvaluationStatus
from task_service.domain.errors import DomainError
from task_service.application.dto.submission import (
    ApplySubmissionResultDTO,
)
from task_service.application.use_cases.submission import FailSubmissionUseCase
from task_service.application.ports import UnitOfWork
from task_service.application.errors import (
    ApplicationError,
    NotFoundError,
    InternalError,
    ValidationError,
)


class ApplySubmissionResultUseCase:
    def __init__(
        self,
        uow: UnitOfWork,
        fail_submission: FailSubmissionUseCase,
    ) -> None:
        self.uow = uow
        self.fail_submission = fail_submission

    async def execute(self, dto: ApplySubmissionResultDTO) -> None:
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

                if submission.status != SubmissionStatus.PENDING:
                    return

                submission.apply_result(
                    tests_passed=dto.tests_passed,
                    tests_total=dto.tests_total,
                    evaluation_status=cast(EvaluationStatus, dto.evaluation_status),
                )
                await uow.submission_repo.update(submission=submission)
                await uow.commit()

        except DomainError as exc:
            await self.fail_submission.execute(id=dto.id)
            raise ValidationError(
                message=exc.message,
                details=exc.details,
            ) from exc

        except ApplicationError:
            await self.fail_submission.execute(id=dto.id)
            raise

        except Exception as exc:
            raise InternalError(
                message="Failed to apply Submission result",
                details={
                    "entity": "submission",
                    "id": dto.id,
                },
            ) from exc
