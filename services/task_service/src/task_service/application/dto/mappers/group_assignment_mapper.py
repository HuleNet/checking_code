from uuid import UUID

from task_service.domain.entities import GroupAssignment
from task_service.application.dto.group_assignment import (
    GroupAssignmentDTO,
    CreateGroupAssignmentDTO,
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
            created_at=domain.created_at,
        )
