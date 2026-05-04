from uuid import UUID

from task_service.domain.errors import DomainError
from task_service.application.dto.submission import SubmissionDTO
from task_service.application.dto.mappers import SubmissionMapper
from task_service.application.models.pagination import CursorPagination, Page
from task_service.application.ports import UnitOfWork
from task_service.application.errors import (
    ApplicationError,
    InternalError,
    ValidationError,
)


class GetSubmissionPageUseCase:
    def __init__(self, uow: UnitOfWork) -> None:
        self.uow = uow

    async def execute(
        self, group_assignment_id: UUID, pagination: CursorPagination
    ) -> Page[SubmissionDTO]:
        try:
            async with self.uow as uow:
                domain_page = await uow.submission_repo.get_page(
                    group_assignment_id=group_assignment_id, pagination=pagination
                )

            return Page(
                items=[
                    SubmissionMapper.to_dto(domain=domain)
                    for domain in domain_page.items
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
                message="Failed to get Submission page",
                details={
                    "entity": "submission",
                    "group_assignment_id": group_assignment_id,
                    "is_page": True,
                },
            ) from exc
