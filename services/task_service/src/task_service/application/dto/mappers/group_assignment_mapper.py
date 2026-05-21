from uuid import UUID

from task_service.domain.entities import GroupAssignment
from task_service.application.dto.group_assignment import (
    GroupAssignmentDTO,
    CreateGroupAssignmentDTO,
    UpdateGroupAssignmentDTO,
)
from task_service.application.dto.mappers import DomainEnumsMapper


class GroupAssignmentMapper:
    @staticmethod
    def to_domain(dto: CreateGroupAssignmentDTO, id: UUID) -> GroupAssignment:
        allowed_languages = set(
            map(
                lambda language: DomainEnumsMapper.map_language(language=language),
                dto.allowed_languages,
            )
        )
        return GroupAssignment(
            id=id,
            group_id=dto.group_id,
            assignment_id=dto.assignment_id,
            allowed_languages=allowed_languages,
            deadline=dto.deadline,
        )

    @staticmethod
    def to_dto(domain: GroupAssignment) -> GroupAssignmentDTO:
        return GroupAssignmentDTO(
            id=domain.id,
            group_id=domain.group_id,
            assignment_id=domain.assignment_id,
            allowed_languages=set(
                map(lambda language: language.value, domain.allowed_languages)
            ),
            deadline=domain.deadline,
            status=domain.status.value,
            finalized_at=domain.finalized_at,
        )

    @staticmethod
    def apply_update(domain: GroupAssignment, update_dto: UpdateGroupAssignmentDTO) -> GroupAssignment:
        return GroupAssignment(
            id=domain.id,
            group_id=update_dto.group_id if update_dto.group_id is not None else domain.group_id,
            assignment_id=update_dto.assignment_id if update_dto.assignment_id is not None else domain.assignment_id,
            allowed_languages=update_dto.allowed_languages if update_dto.allowed_languages is not None else domain.allowed_languages,
            deadline=update_dto.deadline if update_dto.deadline is not None else domain.deadline,
            status=domain.status,
            finalized_at=domain.finalized_at,
        )        
