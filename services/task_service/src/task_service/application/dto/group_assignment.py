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


@dataclass(frozen=True)
class UpdateGroupAssignmentDTO:
    group_id: UUID | None
    assignment_id: UUID | None
    allowed_languages: set[str] | None
    deadline: datetime | None
