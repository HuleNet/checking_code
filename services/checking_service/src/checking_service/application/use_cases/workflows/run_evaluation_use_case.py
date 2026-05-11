from checking_service.domain.errors import DomainError
from checking_service.application.dto.submission import SubmissionDTO
from checking_service.application.dto.evaluation import EvaluationDTO
from checking_service.application.dto.mappers import EvaluationMapper
from checking_service.application.use_cases.test_case import (
    GetTestCasesByAssignmentUseCase,
)
from checking_service.application.use_cases.evaluation import (
    CreateEvaluationUseCase,
    CompleteEvaluationUseCase,
)
from checking_service.application.use_cases.execution_case import (
    CreateExecutionCasesUseCase,
    RunExecutionCasesUseCase,
)
from checking_service.application.ports import UnitOfWork
from checking_service.application.errors import (
    ApplicationError,
    ValidationError,
    InternalError,
)


class RunEvaluationUseCase:
    def __init__(
        self,
        uow: UnitOfWork,
        get_test_cases: GetTestCasesByAssignmentUseCase,
        create_evaluation: CreateEvaluationUseCase,
        complete_evaluation: CompleteEvaluationUseCase,
        create_execution_cases: CreateExecutionCasesUseCase,
        run_execution_cases: RunExecutionCasesUseCase,
    ) -> None:
        self.uow = uow
        self.get_test_cases = get_test_cases
        self.create_evaluation = create_evaluation
        self.complete_evaluation = complete_evaluation
        self.create_execution_cases = create_execution_cases
        self.run_execution_cases = run_execution_cases

    async def execute(self, dto: SubmissionDTO) -> EvaluationDTO:
        try:
            test_cases = await self.get_test_cases.execute(
                assignment_id=dto.assignment_id
            )
            evaluation = self.create_evaluation.execute(
                submission_id=dto.id, tests_total=len(test_cases)
            )
            execution_cases = self.create_execution_cases.execute(
                evaluation_id=evaluation.id, test_cases=test_cases
            )
            updated_execution_cases = await self.run_execution_cases.execute(
                code=dto.code, language=dto.language, execution_cases=execution_cases
            )
            evaluation_dto = self.complete_evaluation.execute(
                evaluation=evaluation, execution_cases=updated_execution_cases
            )
            evaluation = EvaluationMapper.to_domain(dto=evaluation_dto)

            async with self.uow as uow:
                await uow.evaluation_repo.add(evaluation=evaluation)
                await uow.execution_case_repo.add_many(
                    execution_cases=updated_execution_cases
                )
                await uow.commit()

            return evaluation_dto

        except DomainError as exc:
            raise ValidationError(
                message=exc.message,
                details=exc.details,
            ) from exc

        except ApplicationError:
            raise

        except Exception as exc:
            raise InternalError(
                message="Failed to run Evaluation",
                details={
                    "entity": "evaluation",
                },
            ) from exc
