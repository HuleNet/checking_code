from uuid import UUID

from task_service.domain.errors import DomainError
from task_service.application.dto.group_assignment import GroupAssignmentDTO
from task_service.application.dto.mappers import GroupAssignmentMapper
from task_service.application.ports import UnitOfWork
from task_service.application.errors import (
    ApplicationError,
    NotFoundError,
    InternalError,
    ValidationError,
)


class DeleteGroupAssignmentUseCase:
    def __init__(self, uow: UnitOfWork) -> None:
        self.uow = uow

    async def execute(self, id: UUID) -> GroupAssignmentDTO:
        try:
            async with self.uow as uow:
                domain_result = await uow.group_assignment_repo.delete(id=id)

                if domain_result is None:
                    raise NotFoundError(
                        message="GroupAssignment not found",
                        details={
                            "entity": "group_assignment",
                            "id": id,
                        },
                    )

                await uow.commit()

            return GroupAssignmentMapper.to_dto(domain=domain_result)

        except DomainError as exc:
            raise ValidationError(
                message=exc.message,
                details=exc.details,
            ) from exc

        except ApplicationError:
            raise

        except Exception as exc:
            raise InternalError(
                message="Failed to delete GroupAssignment",
                details={
                    "entity": "group_assignment",
                    "id": id,
                },
            ) from exc
