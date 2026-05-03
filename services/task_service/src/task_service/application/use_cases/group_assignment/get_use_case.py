from uuid import UUID

from task_service.application.dto.group_assignment import GroupAssignmentDTO
from task_service.application.dto.mappers import GroupAssignmentMapper
from task_service.application.ports import UnitOfWork
from task_service.application.errors import (
    ApplicationError,
    NotFoundError,
    InternalError,
)


class GetGroupAssignmentUseCase:
    def __init__(self, uow: UnitOfWork) -> None:
        self.uow = uow

    async def execute(self, id: UUID) -> GroupAssignmentDTO:
        try:
            async with self.uow as uow:
                domain_result = await uow.group_assignment_repo.get(id=id)

            if domain_result is None:
                raise NotFoundError(
                    message="GroupAssignment not found",
                    details={
                        "entity": "group_assignment",
                        "id": id,
                    },
                )

            return GroupAssignmentMapper.to_dto(domain=domain_result)

        except ApplicationError:
            raise

        except Exception as exc:
            raise InternalError(
                message="Failed to get GroupAssignment",
                details={
                    "entity": "group_assignment",
                    "id": id,
                },
            ) from exc
