from uuid import uuid4

from task_service.domain.value_objects import CodeHash
from task_service.domain.errors import DomainError
from task_service.application.dto.submission import SubmissionDTO, CreateSubmissionDTO
from task_service.application.dto.mappers import SubmissionMapper
from task_service.application.ports import UnitOfWork, CheckingService
from task_service.application.errors import (
    ApplicationError,
    NotFoundError,
    SubmissionAttemptError,
    InternalError,
    ValidationError,
)


class CreateSubmissionUseCase:
    def __init__(
        self,
        uow: UnitOfWork,
        max_attempts: int,
        checking_service: CheckingService,
    ) -> None:
        self.uow = uow
        self.max_attempts = max_attempts
        self.checking_service = checking_service

    async def execute(self, dto: CreateSubmissionDTO) -> SubmissionDTO:
        try:
            async with self.uow as uow:
                group_assignment = await uow.group_assignment_repo.get(
                    id=dto.group_assignment_id
                )

                if group_assignment is None:
                    raise NotFoundError(
                        message="GroupAssignment not found",
                        details={
                            "entity": "group_assignment",
                            "id": dto.group_assignment_id,
                        },
                    )

                code_hash = CodeHash.from_code(code=dto.code)
                attempt_number = await uow.submission_repo.get_attempt_number_and_check(
                    student_id=dto.student_id,
                    group_assignment_id=dto.group_assignment_id,
                    code_hash=code_hash.value,
                    max_attempts=self.max_attempts,
                )

                if attempt_number == 0:
                    raise SubmissionAttemptError(
                        message="Max attempts exceeded",
                        details={
                            "entity": "submission",
                            "reason": "max_attempts_exceeded",
                        },
                    )

                if attempt_number is None:
                    raise SubmissionAttemptError(
                        message="Submission with exact code already exists",
                        details={
                            "entity": "submission",
                            "reason": "code_duplicate",
                        },
                    )

                submission = SubmissionMapper.to_domain(
                    dto=dto,
                    id=uuid4(),
                    assignment_id=group_assignment.assignment_id,
                    code_hash=code_hash,
                    attempt_number=attempt_number,
                )
                group_assignment.ensure_language_allowed(language=submission.language)
                group_assignment.ensure_not_expired(now=submission.created_at)
                domain_result = await uow.submission_repo.add(submission=submission)
                await uow.commit()

            await self.checking_service.create_evaluation(
                submission_id=submission.id,
                assignment_id=submission.assignment_id,
                code=submission.code,
                language=submission.language.value,
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
                message="Failed to create Submission",
                details={
                    "entity": "submission",
                },
            ) from exc
