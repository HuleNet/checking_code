from task_service.domain.errors import DomainError
from task_service.application.dto.assignment import AssignmentDTO
from task_service.application.dto.mappers import AssignmentMapper
from task_service.application.models.pagination import CursorPagination, Page
from task_service.application.ports import UnitOfWork
from task_service.application.errors import (
    ApplicationError,
    InternalError,
    ValidationError,
)


class GetAssignmentPageUseCase:
    def __init__(self, uow: UnitOfWork) -> None:
        self.uow = uow

    async def execute(self, pagination: CursorPagination) -> Page[AssignmentDTO]:
        try:
            async with self.uow as uow:
                domain_page = await uow.assignment_repo.get_page(pagination=pagination)

            return Page(
                items=[
                    AssignmentMapper.to_dto(domain=domain)
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
                message="Failed to get Assignment page",
                details={
                    "entity": "assignment",
                    "is_page": True,
                },
            ) from exc
