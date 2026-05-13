from uuid import UUID, uuid4

from checking_service.domain.entities import ExecutionCase, TestCase
from checking_service.domain.errors import DomainError
from checking_service.application.dto.mappers import ExecutionCaseMapper
from checking_service.application.errors import (
    ApplicationError,
    InternalError,
    ValidationError,
)


class CreateExecutionCasesUseCase:
    def execute(
        self, evaluation_id: UUID, test_cases: list[TestCase]
    ) -> list[ExecutionCase]:
        try:
            execution_cases = [
                ExecutionCaseMapper.to_domain(
                    id=uuid4(), evaluation_id=evaluation_id, test_case=test_case
                )
                for test_case in test_cases
            ]
            return execution_cases

        except DomainError as exc:
            raise ValidationError(
                message=exc.message,
                details=exc.details,
            ) from exc

        except ApplicationError:
            raise

        except Exception as exc:
            raise InternalError(
                message="Failed to create ExecutionCases",
                details={
                    "entity": "execution_case",
                    "evaluation_id": evaluation_id,
                },
            ) from exc
