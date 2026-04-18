from uuid import uuid4

from checking_service.application.dto.submission import PreviewSubmissionDTO
from checking_service.application.dto.evaluation import PreviewEvaluationDTO
from checking_service.application.dto.mappers import (
    SubmissionMapper,
    ExecutionCaseMapper,
)
from checking_service.application.models.factories import ExecutionCaseFactory
from checking_service.application.ports.repositories import InputCaseRepository
from checking_service.application.services import ExecutionService
from checking_service.application.errors import NotFoundError


class PreviewRunUseCase:
    def __init__(
        self,
        input_case_repo: InputCaseRepository,
        execution_service: ExecutionService,
    ) -> None:
        self.input_case_repo = input_case_repo
        self.execution_service = execution_service

    async def execute(self, submission: PreviewSubmissionDTO) -> PreviewEvaluationDTO:
        submission_domain = SubmissionMapper.to_domain_from_preview(dto=submission)
        input_cases = await self.input_case_repo.get_by_assignment(
            assignment_id=submission_domain.assignment_id
        )

        if not input_cases:
            raise NotFoundError(
                message="InputCases not found",
                details={
                    "dry_run": True,
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
            execution_cases = await self.execution_service.execute(
                code=submission_domain.code,
                language=submission_domain.language,
                execution_cases=execution_cases,
            )

        # !ЗАМЕНИТЬ НА INFRA-ERROR!
        except Exception:
            raise

        status, summary_execution_case = self.execution_service.dry_summarize(
            execution_cases=execution_cases
        )
        passed_tests_count = self.execution_service.dry_count_passed(execution_cases)
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
