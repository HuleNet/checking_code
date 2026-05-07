from dataclasses import dataclass
from uuid import UUID
from datetime import datetime


@dataclass(frozen=True)
class GroupAssignmentDTO:
    id: UUID
    group_id: UUID
    assignment_id: UUID
    allowed_languages: set[str]
    deadline: datetime
    status: str
    finalized_at: datetime | None


@dataclass(frozen=True)
class CreateGroupAssignmentDTO:
    group_id: UUID
    assignment_id: UUID
    allowed_languages: set[str]
    deadline: datetime
