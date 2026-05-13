from uuid import UUID, uuid4

from checking_service.domain.entities import Evaluation
from checking_service.domain.errors import DomainError
from checking_service.application.errors import (
    ApplicationError,
    InternalError,
    ValidationError,
)


class CreateEvaluationUseCase:
    def execute(self, submission_id: UUID, tests_total: int) -> Evaluation:
        try:
            evaluation = Evaluation(
                id=uuid4(), tests_total=tests_total, submission_id=submission_id
            )
            return evaluation

        except DomainError as exc:
            raise ValidationError(
                message=exc.message,
                details=exc.details,
            ) from exc

        except ApplicationError:
            raise

        except Exception as exc:
            raise InternalError(
                message="Failed to create Evaluation",
                details={
                    "entity": "evaluation",
                    "submission": submission_id,
                },
            ) from exc
