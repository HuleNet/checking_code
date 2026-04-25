from uuid import uuid4

from checking_service.application.dto.submission import SubmissionDTO
from checking_service.application.dto.evaluation import (
    CreateEvaluationDTO,
    EvaluationDTO,
)
from checking_service.application.dto.mappers import (
    SubmissionMapper,
    EvaluationMapper,
)
from checking_service.application.models.factories import (
    ExecutionCaseFactory,
    OutboxMessageFactory,
)
from checking_service.application.ports import UnitOfWork
from checking_service.application.errors import (
    ApplicationError,
    NotFoundError,
    InternalError,
)


class StartEvaluationUseCase:
    def __init__(self, uow: UnitOfWork) -> None:
        self.uow = uow

    async def execute(self, submission: SubmissionDTO) -> EvaluationDTO:
        try:
            submission_domain = SubmissionMapper.to_domain(dto=submission)

            async with self.uow as uow:
                input_cases = await uow.input_case_repo.get_by_assignment(
                    assignment_id=submission_domain.assignment_id
                )

                if not input_cases:
                    raise NotFoundError(
                        message="InputCases not found",
                        details={
                            "entity": "input_case",
                            "assignment_id": submission_domain.assignment_id,
                        },
                    )

                evaluation_domain = EvaluationMapper.to_domain(
                    dto=CreateEvaluationDTO(
                        submission_id=submission_domain.id,
                        total_tests_count=len(input_cases),
                    ),
                    id=uuid4(),
                )
                execution_cases = [
                    ExecutionCaseFactory.create_execution_case(
                        id=uuid4(),
                        evaluation_id=evaluation_domain.id,
                        input_case=input_case,
                    )
                    for input_case in input_cases
                ]
                await uow.evaluation_repo.add(evaluation=evaluation_domain)
                await uow.execution_case_repo.add_many(execution_cases=execution_cases)
                outbox_event = OutboxMessageFactory.create_run_evaluation_event(
                    evaluation_id=evaluation_domain.id,
                    submission=submission_domain,
                )
                outbox_message = OutboxMessageFactory.create_run_evaluation_message(
                    id=uuid4(),
                    event=outbox_event,
                )
                await uow.outbox_repo.add(message=outbox_message)
                await uow.commit()

            return EvaluationMapper.to_dto(domain=evaluation_domain)

        except ApplicationError:
            raise

        except Exception as exc:
            raise InternalError(
                message="Failed to start Evaluation",
                details={
                    "entity": "evaluation",
                    "assignment_id": submission.assignment_id,
                },
            ) from exc
