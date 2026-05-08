from uuid import uuid4, UUID
from typing import Any

from task_service.domain.value_objects import SubmissionStatus
from task_service.domain.errors import DomainError
from task_service.domain.entities import FinalResult
from task_service.domain.services import ScoringService
from task_service.application.dto.final_result import FinalResultDTO
from task_service.application.dto.mappers import FinalResultMapper
from task_service.application.ports import UnitOfWork
from task_service.application.errors import (
    ApplicationError,
    NotFoundError,
    InternalError,
    ValidationError,
)


class CreateFinalResultsUseCase:
    def __init__(self, uow: UnitOfWork, scoring_service: ScoringService) -> None:
        self.uow = uow
        self.scoring_service = scoring_service

    async def execute(self, group_assignment_id: UUID) -> list[FinalResultDTO]:
        try:
            async with self.uow as uow:
                submissions = await uow.submission_repo.get_by_group_assignment(
                    group_assignment_id=group_assignment_id
                )

                if not submissions:
                    raise NotFoundError(
                        message="Submissions not found",
                        details={
                            "entity": "submission",
                            "group_assignment_id": group_assignment_id,
                        },
                    )

                final_results = []
                best_by_student: dict[UUID, Any] = {}

                for submission in submissions:
                    if submission.status != SubmissionStatus.COMPLETED:
                        continue

                    current = best_by_student.get(submission.student_id)

                    if not current:
                        best_by_student[submission.student_id] = submission
                        continue

                    if submission.tests_passed > current.tests_passed:
                        best_by_student[submission.student_id] = submission

                    elif (
                        submission.tests_passed == current.tests_passed
                        and submission.created_at < current.created_at
                    ):
                        best_by_student[submission.student_id] = submission

                for student_id, submission in best_by_student.items():
                    if (
                        submission.tests_passed is None
                        or submission.tests_total is None
                    ):
                        continue

                    final_results.append(
                        FinalResult(
                            id=uuid4(),
                            group_assignment_id=submission.group_assignment_id,
                            student_id=student_id,
                            submission_id=submission.id,
                            score=self.scoring_service.calculate(
                                tests_passed=submission.tests_passed,
                                tests_total=submission.tests_total,
                                attempt_number=submission.attempt_number,
                            ),
                            attempt_number=submission.attempt_number,
                            tests_total=submission.tests_total,
                            tests_passed=submission.tests_passed,
                            plagiarism_score=1.0,  # заглушка
                            plagiarism_flag=True,  # заглушка
                        )
                    )

                await uow.final_result_repo.add_many(final_results=final_results)
                await uow.commit()

            return [FinalResultMapper.to_dto(domain=domain) for domain in final_results]

        except DomainError as exc:
            raise ValidationError(
                message=exc.message,
                details=exc.details,
            ) from exc

        except ApplicationError:
            raise

        except Exception as exc:
            raise InternalError(
                message="Failed to create FinalResults",
                details={
                    "entity": "final_result",
                    "group_assignment_id": group_assignment_id,
                },
            ) from exc
