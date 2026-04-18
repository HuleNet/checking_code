from uuid import uuid4

from checking_service.application.dto.submission import SubmissionDTO
from checking_service.application.dto.evaluation import (
    CreateEvaluationDTO,
    EvaluationDTO,
)
from checking_service.application.mappers import (
    SubmissionMapper,
    EvaluationMapper,
    ExecutionCaseMapper,
    OutboxMessageMapper,
)
from checking_service.application.ports import UnitOfWork
from checking_service.application.errors import NotFoundError


class StartEvaluationUseCase:
    def __init__(self, uow: UnitOfWork) -> None:
        self.uow = uow

    async def execute(self, submission: SubmissionDTO) -> EvaluationDTO:
        submission_domain = SubmissionMapper.to_domain(dto=submission)

        async with self.uow as uow:
            input_cases = await uow.input_case_repo.get_by_assignment(
                assignment_id=submission_domain.assignment_id
            )

            if not input_cases:
                raise NotFoundError(
                    message="InputCases not found",
                    details={
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
                ExecutionCaseMapper.to_domain_from_input_case(
                    input_case=input_case,
                    id=uuid4(),
                    evaluation_id=evaluation_domain.id,
                )
                for input_case in input_cases
            ]
            await uow.evaluation_repo.add(evaluation=evaluation_domain)
            await uow.execution_case_repo.add_many(execution_cases=execution_cases)
            outbox_message = OutboxMessageMapper.map_run_evaluation_message(
                submission=submission_domain,
                id=uuid4(),
                evaluation_id=evaluation_domain.id,
            )
            await uow.outbox_repo.add(message=outbox_message)
            await uow.commit()

        return EvaluationMapper.to_dto(domain=evaluation_domain)
