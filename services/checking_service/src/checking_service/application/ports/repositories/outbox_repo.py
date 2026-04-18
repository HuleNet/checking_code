from typing import Protocol

from checking_service.application.models.outbox import OutboxMessage


class OutboxRepository(Protocol):
    async def add(self, message: OutboxMessage) -> None: ...
