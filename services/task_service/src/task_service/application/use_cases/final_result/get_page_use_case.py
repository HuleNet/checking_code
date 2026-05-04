from uuid import UUID

from task_service.domain.errors import DomainError
from task_service.application.dto.final_result import FinalResultDTO
from task_service.application.dto.mappers import FinalResultMapper
from task_service.application.models.pagination import CursorPagination, Page
from task_service.application.ports import UnitOfWork
from task_service.application.errors import (
    ApplicationError,
    InternalError,
    ValidationError,
)


class GetFinalResultPageUseCase:
    def __init__(self, uow: UnitOfWork) -> None:
        self.uow = uow

    async def execute(
        self, group_assignment_id: UUID, pagination: CursorPagination
    ) -> Page[FinalResultDTO]:
        try:
            async with self.uow as uow:
                domain_page = await uow.final_result_repo.get_page(
                    group_assignment_id=group_assignment_id, pagination=pagination
                )

            return Page(
                items=[
                    FinalResultMapper.to_dto(domain=domain)
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
                message="Failed to get FinalResult page",
                details={
                    "entity": "final_result",
                    "group_assignment_id": group_assignment_id,
                    "is_page": True,
                },
            ) from exc
