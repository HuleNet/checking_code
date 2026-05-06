from typing import Any

from task_service.domain.entities import GroupAssignment
from task_service.infrastructure.db.models import GroupAssignmentORM


class GroupAssignmentMapper:
    @staticmethod
    def to_domain(orm: GroupAssignmentORM) -> GroupAssignment:
        return GroupAssignment(
            id=orm.id,
            group_id=orm.group_id,
            assignment_id=orm.assignment_id,
            allowed_languages=set(orm.allowed_languages),
            deadline=orm.deadline,
            created_at=orm.created_at,
        )

    @staticmethod
    def to_dict(domain: GroupAssignment) -> dict[str, Any]:
        return {
            "id": domain.id,
            "group_id": domain.group_id,
            "assignment_id": domain.assignment_id,
            "allowed_languages": list(domain.allowed_languages),
            "deadline": domain.deadline,
            "created_at": domain.created_at,
        }
