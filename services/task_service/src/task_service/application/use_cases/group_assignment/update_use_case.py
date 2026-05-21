from uuid import UUID

from task_service.domain.value_objects import GroupAssignmentStatus
from task_service.domain.errors import DomainError
from task_service.application.dto.group_assignment import GroupAssignmentDTO, UpdateGroupAssignmentDTO
from task_service.application.dto.mappers import GroupAssignmentMapper
from task_service.application.ports import UnitOfWork
from task_service.application.errors import (
    ApplicationError,
    NotFoundError,
    InternalError,
    ValidationError,
)


class UpdateGroupAssignmentUseCase:
    def __init__(self, uow: UnitOfWork) -> None:
        self.uow = uow

    async def execute(self, id: UUID, dto: UpdateGroupAssignmentDTO) -> GroupAssignmentDTO:
        try:
            async with self.uow as uow:
                domain = await uow.group_assignment_repo.get(id=id)

                if domain is None:
                    raise NotFoundError(
                        message="GroupAssignment not found",
                        details={
                            "entity": "group_assignment",
                            "id": id,
                        },
                    )
                
                if domain.status == GroupAssignmentStatus.FINALIZED:
                    raise ValidationError(
                        message="GroupAssignment must be in ACTIVE status for update",
                        details={
                            "entity": "group_assignment",
                            "id": id,
                        }
                    )

                updating_domain = GroupAssignmentMapper.apply_update(
                    domain=domain, update_dto=dto
                )
                result_domain = await uow.group_assignment_repo.update(
                    group_assignment=updating_domain
                )
                await uow.commit()

            return GroupAssignmentMapper.to_dto(domain=result_domain)

        except DomainError as exc:
            raise ValidationError(
                message=exc.message,
                details=exc.details,
            ) from exc

        except ApplicationError:
            raise

        except Exception as exc:
            raise InternalError(
                message="Failed to update GroupAssignment",
                details={
                    "entity": "group_assignment",
                    "id": id,
                },
            ) from exc
