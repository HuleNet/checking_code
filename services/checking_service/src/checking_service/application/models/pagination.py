from dataclasses import dataclass
from typing import Any, Generic, TypeVar


T = TypeVar("T")


@dataclass(frozen=True)
class CursorPagination:
    limit: int
    cursor: dict[str, Any] | None = None


@dataclass(frozen=True)
class Page(Generic[T]):
    items: list[T]
    next_cursor: dict[str, Any] | None
