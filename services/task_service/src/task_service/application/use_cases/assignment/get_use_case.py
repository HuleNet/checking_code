from uuid import UUID

from task_service.application.dto.assignment import AssignmentDTO
from task_service.application.dto.mappers import AssignmentMapper
from task_service.application.ports.unit_of_work import UnitOfWork
from task_service.application.errors import (
    ApplicationError,
    NotFoundError,
    InternalError,
)


class GetAssignmentUseCase:
    def __init__(self, uow: UnitOfWork) -> None:
        self.uow = uow

    async def execute(self, id: UUID) -> AssignmentDTO:
        try:
            async with self.uow as uow:
                domain_result = await uow.assignment_repo.get(id=id)

            if domain_result is None:
                raise NotFoundError(
                    message="Assignment not found",
                    details={
                        "entity": "assignment",
                        "id": id,
                    },
                )

            return AssignmentMapper.to_dto(domain=domain_result)

        except ApplicationError:
            raise

        except Exception as exc:
            raise InternalError(
                message="Failed to get Assignment",
                details={
                    "entity": "assignment",
                    "id": id,
                },
            ) from exc
