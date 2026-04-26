from dataclasses import dataclass, field
from uuid import UUID
from datetime import datetime, timezone


@dataclass(frozen=True)
class GroupAssignment:
    id: UUID
    group_id: UUID
    assignment_id: UUID
    allowed_languages: set[str]
    deadline: datetime
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
