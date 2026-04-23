from uuid import uuid4

from checking_service.application.dto.submission import PreviewSubmissionDTO
from checking_service.application.dto.evaluation import PreviewEvaluationDTO
from checking_service.application.dto.mappers import (
    SubmissionMapper,
    ExecutionCaseMapper,
)
from checking_service.application.models.factories import ExecutionCaseFactory
from checking_service.application.ports import UnitOfWork
from checking_service.application.services import EvaluationService
from checking_service.application.errors import (
    NotFoundError,
    ServiceExecutionError,
    InternalServiceError,
)


class PreviewRunUseCase:
    def __init__(
        self,
        uow: UnitOfWork,
        evaluation_service: EvaluationService,
    ) -> None:
        self.uow = uow
        self.evaluation_service = evaluation_service

    async def execute(self, submission: PreviewSubmissionDTO) -> PreviewEvaluationDTO:
        submission_domain = SubmissionMapper.to_domain_from_preview(dto=submission)

        async with self.uow as uow:
            input_cases = await uow.input_case_repo.get_by_assignment(
                assignment_id=submission_domain.assignment_id
            )

        if not input_cases:
            raise NotFoundError(
                message="InputCases not found",
                details={
                    "preview_run": True,
                    "assignment_id": submission_domain.assignment_id,
                },
            )

        fake_evaluation_id = uuid4()
        execution_cases = [
            ExecutionCaseFactory.create_execution_case(
                id=uuid4(),
                evaluation_id=fake_evaluation_id,
                input_case=input_case,
            )
            for input_case in input_cases
        ]

        try:
            execution_cases = await self.evaluation_service.execute(
                code=submission_domain.code,
                language=submission_domain.language,
                execution_cases=execution_cases,
            )

        except ServiceExecutionError as exc:
            exc.details["preview_run"] = True
            raise

        except Exception as exc:
            raise InternalServiceError(
                message="Unexpected execution failure",
                details={
                    "preview_run": True,
                },
            ) from exc

        status, summary_execution_case = self.evaluation_service.summarize(
            execution_cases=execution_cases
        )
        passed_tests_count = self.evaluation_service.count_passed_tests(
            execution_cases=execution_cases
        )
        return PreviewEvaluationDTO(
            total_tests_count=len(execution_cases),
            passed_tests_count=passed_tests_count,
            status=status,
            summary_execution_case=ExecutionCaseMapper.to_dto(
                domain=summary_execution_case
            )
            if summary_execution_case
            else None,
        )
