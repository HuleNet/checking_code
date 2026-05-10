from uuid import UUID

from checking_service.domain.errors import DomainError
from checking_service.application.dto.test_case import TestCaseDTO
from checking_service.application.dto.mappers import TestCaseMapper
from checking_service.application.ports import UnitOfWork
from checking_service.application.errors import (
    ApplicationError,
    InternalError,
    ValidationError,
)


class GetTestCasesByAssignmentUseCase:
    def __init__(self, uow: UnitOfWork) -> None:
        self.uow = uow

    async def execute(self, assignment_id: UUID) -> list[TestCaseDTO]:
        try:
            async with self.uow as uow:
                domain_results = await uow.test_case_repo.get_by_assignment(
                    assignment_id=assignment_id
                )

            return [TestCaseMapper.to_dto(domain=domain) for domain in domain_results]

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
