from uuid import UUID

from task_service.domain.entities import Assignment
from task_service.application.dto.assignment import (
    AssignmentDTO,
    CreateAssignmentDTO,
    UpdateAssignmentDTO,
)


class AssignmentMapper:
    @staticmethod
    def to_domain(dto: CreateAssignmentDTO, id: UUID) -> Assignment:
        return Assignment(
            id=id,
            title=dto.title,
            description=dto.description,
        )

    @staticmethod
    def to_dto(domain: Assignment) -> AssignmentDTO:
        return AssignmentDTO(
            id=domain.id,
            title=domain.title,
            description=domain.description,
            created_at=domain.created_at,
        )

    @staticmethod
    def apply_update(domain: Assignment, update_dto: UpdateAssignmentDTO) -> Assignment:
        return Assignment(
            id=domain.id,
            title=update_dto.title if update_dto.title is not None else domain.title,
            description=update_dto.description
            if update_dto.description is not None
            else domain.description,
        )
