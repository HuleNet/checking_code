from dataclasses import dataclass
from uuid import UUID
from datetime import datetime


@dataclass(frozen=True)
class AssignmentDTO:
    id: UUID
    title: str
    description: str
    created_at: datetime


@dataclass(frozen=True)
class CreateAssignmentDTO:
    title: str
    description: str


@dataclass(frozen=True)
class UpdateAssignmentDTO:
    title: str | None = None
    description: str | None = None
