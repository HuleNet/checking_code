from dataclasses import dataclass, field
from uuid import UUID, uuid4
from datetime import datetime, timezone


@dataclass(frozen=True, kw_only=True)
class DomainEvent:
    id: UUID = field(default_factory=uuid4)
    occurred_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
