from dataclasses import dataclass
from uuid import UUID
from datetime import datetime
from typing import Any


@dataclass(frozen=True)
class OutboxMessage:
    id: UUID
    event_type: str
    payload: dict[str, Any]
    occurred_at: datetime
    processed_at: datetime | None = None
