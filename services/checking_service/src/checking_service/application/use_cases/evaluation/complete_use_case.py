from checking_service.domain.entities import Evaluation, ExecutionCase
from checking_service.domain.services import JudgeService
from checking_service.domain.errors import DomainError
from checking_service.application.dto.evaluation import EvaluationDTO
from checking_service.application.dto.mappers import EvaluationMapper
from checking_service.application.errors import (
    ApplicationError,
    InternalError,
    ValidationError,
)


class CompleteEvaluationUseCase:
    def __init__(self, judge: JudgeService) -> None:
        self.judge = judge

    def execute(
        self, evaluation: Evaluation, execution_cases: list[ExecutionCase]
    ) -> EvaluationDTO:
        try:
            evaluation_result = self.judge.evaluate(execution_cases=execution_cases)
            evaluation.apply_results(evaluation_result=evaluation_result)
            return EvaluationMapper.to_dto(domain=evaluation)

        except DomainError as exc:
            raise ValidationError(
                message=exc.message,
                details=exc.details,
            ) from exc

        except ApplicationError:
            raise

        except Exception as exc:
            raise InternalError(
                message="Failed to complete Evaluation",
                details={
                    "entity": "evaluation",
                    "id": evaluation.id,
                },
            ) from exc
