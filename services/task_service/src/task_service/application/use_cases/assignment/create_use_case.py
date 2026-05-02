from uuid import uuid4

from task_service.application.dto.assignment import (
    AssignmentDTO,
    CreateAssignmentDTO,
)
from task_service.application.dto.mappers import AssignmentMapper
from task_service.application.ports import UnitOfWork
from task_service.application.errors import ApplicationError, InternalError


class CreateAssignmentUseCase:
    def __init__(self, uow: UnitOfWork) -> None:
        self.uow = uow

    async def execute(self, dto: CreateAssignmentDTO) -> AssignmentDTO:
        try:
            async with self.uow as uow:
                assignment = AssignmentMapper.to_domain(dto=dto, id=uuid4())
                domain_result = await uow.assignment_repo.add(assignment=assignment)
                await uow.commit()

            return AssignmentMapper.to_dto(domain=domain_result)

        except ApplicationError:
            raise

        except Exception as exc:
            raise InternalError(
                message="Failed to create Assignment",
                details={
                    "entity": "assignment",
                },
            ) from exc
