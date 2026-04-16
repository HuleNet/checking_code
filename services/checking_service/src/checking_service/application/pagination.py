from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class Cursor:
    id: UUID


@dataclass(frozen=True)
class Pagination:
    limit: int
    cursor: Cursor | None = None
