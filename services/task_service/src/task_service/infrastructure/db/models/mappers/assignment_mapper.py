from typing import Any

from task_service.domain.entities import Assignment
from task_service.infrastructure.db.models import AssignmentORM


class AssignmentMapper:
    @staticmethod
    def to_domain(orm: AssignmentORM) -> Assignment:
        return Assignment(
            id=orm.id,
            title=orm.title,
            description=orm.description,
            created_at=orm.created_at,
        )

    @staticmethod
    def to_dict(domain: Assignment) -> dict[str, Any]:
        return {
            "id": domain.id,
            "title": domain.title,
            "description": domain.description,
            "created_at": domain.created_at,
        }
