from uuid import UUID

from task_service.application.dto.group_assignment import GroupAssignmentDTO
from task_service.application.dto.mappers import GroupAssignmentMapper
from task_service.application.models.pagination import CursorPagination, Page
from task_service.application.ports import UnitOfWork
from task_service.application.errors import ApplicationError, InternalError


class GetGroupAssignmentPageUseCase:
    def __init__(self, uow: UnitOfWork) -> None:
        self.uow = uow

    async def execute(
        self, group_id: UUID, pagination: CursorPagination
    ) -> Page[GroupAssignmentDTO]:
        try:
            async with self.uow as uow:
                domain_page = await uow.group_assignment_repo.get_page(
                    group_id=group_id, pagination=pagination
                )

            return Page(
                items=[
                    GroupAssignmentMapper.to_dto(domain=domain)
                    for domain in domain_page.items
                ],
                next_cursor=domain_page.next_cursor,
            )

        except ApplicationError:
            raise

        except Exception as exc:
            raise InternalError(
                message="Failed to get GroupAssignment page",
                details={
                    "entity": "group_assignment",
                    "group_id": group_id,
                    "is_page": True,
                },
            ) from exc
