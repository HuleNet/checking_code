from uuid import uuid4

from task_service.domain.errors import DomainError
from task_service.application.dto.group_assignment import (
    GroupAssignmentDTO,
    CreateGroupAssignmentDTO,
)
from task_service.application.dto.mappers import GroupAssignmentMapper
from task_service.application.ports import UnitOfWork
from task_service.application.errors import (
    ApplicationError,
    NotFoundError,
    InternalError,
    ValidationError,
)


class CreateGroupAssignmentUseCase:
    def __init__(self, uow: UnitOfWork) -> None:
        self.uow = uow

    async def execute(self, dto: CreateGroupAssignmentDTO) -> GroupAssignmentDTO:
        try:
            async with self.uow as uow:
                assignment = await uow.assignment_repo.get(id=dto.assignment_id)

                if assignment is None:
                    raise NotFoundError(
                        message="Assignment not found",
                        details={
                            "entity": "assignment",
                            "id": dto.assignment_id,
                        },
                    )

                group_assignment = GroupAssignmentMapper.to_domain(dto=dto, id=uuid4())
                domain_result = await uow.group_assignment_repo.add(
                    group_assignment=group_assignment
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
                message="Failed to create GroupAssignment",
                details={
                    "entity": "group_assignment",
                },
            ) from exc
