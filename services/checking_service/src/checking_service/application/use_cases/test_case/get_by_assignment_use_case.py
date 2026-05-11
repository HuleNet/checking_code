from uuid import UUID

from checking_service.domain.entities import TestCase
from checking_service.domain.errors import DomainError
from checking_service.application.ports import UnitOfWork
from checking_service.application.errors import (
    ApplicationError,
    InternalError,
    ValidationError,
)


class GetTestCasesByAssignmentUseCase:
    def __init__(self, uow: UnitOfWork) -> None:
        self.uow = uow

    async def execute(self, assignment_id: UUID) -> list[TestCase]:
        try:
            async with self.uow as uow:
                test_cases = await uow.test_case_repo.get_by_assignment(
                    assignment_id=assignment_id
                )

            return test_cases

        except DomainError as exc:
            raise ValidationError(
                message=exc.message,
                details=exc.details,
            ) from exc

        except ApplicationError:
            raise

        except Exception as exc:
            raise InternalError(
                message="Failed to get TestCases",
                details={
                    "entity": "test_case",
                    "assignment_id": assignment_id,
                    "is_page": False,
                },
            ) from exc
