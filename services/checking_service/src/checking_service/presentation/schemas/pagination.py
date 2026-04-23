from typing import Generic, TypeVar, Any

from checking_service.presentation.schemas import BaseSchema


T = TypeVar("T")


class CursorPaginationRequest(BaseSchema):
    limit: int = 20
    cursor: dict[str, Any] | None = None


class CursorPage(BaseSchema, Generic[T]):
    items: list[T]
    next_cursor: dict[str, Any] | None
