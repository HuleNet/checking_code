from dataclasses import dataclass, field
from uuid import UUID
from datetime import datetime, timezone


@dataclass(frozen=True)
class Assignment:
    id: UUID
    title: str
    description: str
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
