from uuid import UUID

from checking_service.domain.errors import DomainError
from checking_service.application.dto.test_case import TestCaseDTO
from checking_service.application.dto.mappers import TestCaseMapper
from checking_service.application.models.pagination import CursorPagination, Page
from checking_service.application.ports import UnitOfWork
from checking_service.application.errors import (
    ApplicationError,
    InternalError,
    ValidationError,
)


class GetTestCasePageUseCase:
    def __init__(self, uow: UnitOfWork) -> None:
        self.uow = uow

    async def execute(
        self, assignment_id: UUID, pagination: CursorPagination
    ) -> Page[TestCaseDTO]:
        try:
            async with self.uow as uow:
                domain_page = await uow.test_case_repo.get_page(
                    assignment_id=assignment_id, pagination=pagination
                )

            return Page(
                items=[
                    TestCaseMapper.to_dto(domain=domain) for domain in domain_page.items
                ],
                next_cursor=domain_page.next_cursor,
            )

        except DomainError as exc:
            raise ValidationError(
                message=exc.message,
                details=exc.details,
            ) from exc

        except ApplicationError:
            raise

        except Exception as exc:
            raise InternalError(
                message="Failed to get TestCase page",
                details={
                    "entity": "test_case",
                    "assignment_id": assignment_id,
                    "is_page": True,
                },
            ) from exc
