from typing import Generic, TypeVar, Any

from task_service.presentation.schemas.base_schema import BaseSchema


T = TypeVar("T")


class PageResponse(BaseSchema, Generic[T]):
    items: list[T]
    next_cursor: dict[str, Any] | None
