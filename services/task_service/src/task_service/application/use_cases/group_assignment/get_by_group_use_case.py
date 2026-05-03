from uuid import UUID

from task_service.application.dto.group_assignment import GroupAssignmentDTO
from task_service.application.dto.mappers import GroupAssignmentMapper
from task_service.application.ports import UnitOfWork
from task_service.application.errors import ApplicationError, InternalError


class GetGroupAssignmentsByGroupUseCase:
    def __init__(self, uow: UnitOfWork) -> None:
        self.uow = uow

    async def execute(self, group_id: UUID) -> list[GroupAssignmentDTO]:
        try:
            async with self.uow as uow:
                domain_results = await uow.group_assignment_repo.get_by_group(
                    group_id=group_id
                )

            return [
                GroupAssignmentMapper.to_dto(domain=domain) for domain in domain_results
            ]

        except ApplicationError:
            raise

        except Exception as exc:
            raise InternalError(
                message="Failed to get GroupAssignments",
                details={
                    "entity": "group_assignment",
                    "group_id": group_id,
                    "is_page": False,
                },
            ) from exc
