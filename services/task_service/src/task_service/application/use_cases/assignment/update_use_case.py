from uuid import UUID

from task_service.domain.errors import DomainError
from task_service.application.dto.assignment import AssignmentDTO, UpdateAssignmentDTO
from task_service.application.dto.mappers import AssignmentMapper
from task_service.application.ports import UnitOfWork
from task_service.application.errors import (
    ApplicationError,
    NotFoundError,
    InternalError,
    ValidationError,
)


class UpdateAssignmentUseCase:
    def __init__(self, uow: UnitOfWork) -> None:
        self.uow = uow

    async def execute(self, id: UUID, dto: UpdateAssignmentDTO) -> AssignmentDTO:
        try:
            async with self.uow as uow:
                domain = await uow.assignment_repo.get(id=id)

                if domain is None:
                    raise NotFoundError(
                        message="Assignment not found",
                        details={
                            "entity": "assignment",
                            "id": id,
                        },
                    )

                updating_domain = AssignmentMapper.apply_update(
                    domain=domain, update_dto=dto
                )
                result_domain = await uow.assignment_repo.update(
                    assignment=updating_domain
                )
                await uow.commit()

            return AssignmentMapper.to_dto(domain=result_domain)

        except DomainError as exc:
            raise ValidationError(
                message=exc.message,
                details=exc.details,
            ) from exc

        except ApplicationError:
            raise

        except Exception as exc:
            raise InternalError(
                message="Failed to update Assignment",
                details={
                    "entity": "assignment",
                    "id": id,
                },
            ) from exc
