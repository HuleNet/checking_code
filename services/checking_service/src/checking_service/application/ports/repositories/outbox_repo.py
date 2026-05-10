from typing import Protocol
from uuid import UUID

from checking_service.application.models.outbox import OutboxMessage


class OutboxRepository(Protocol):
    async def add(self, message: OutboxMessage) -> None: ...

    async def get_unprocessed(self, limit: int) -> list[OutboxMessage]: ...

    async def mark_processed(self, ids: list[UUID]) -> None: ...
