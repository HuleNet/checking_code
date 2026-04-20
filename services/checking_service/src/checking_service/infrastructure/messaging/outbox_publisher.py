from asyncio import sleep

from checking_service.application.models.outbox import OutboxMessage
from checking_service.application.ports import UnitOfWork
from checking_service.infrastructure.messaging import CeleryDispatcher


class OutboxPublisher:
    def __init__(
        self, uow: UnitOfWork, dispatcher: CeleryDispatcher, batch_size: int = 10
    ) -> None:
        self.uow = uow
        self.dispatcher = dispatcher
        self.batch_size = batch_size

    async def run_forever(self):
        while True:
            await self._process_batch()
            await sleep(1)

    async def _process_batch(self) -> None:
        async with self.uow as uow:
            messages = await uow.outbox_repo.claim_batch(self.batch_size)
            await uow.commit()

        for message in messages:
            await self._handle_message(message=message)

    async def _handle_message(self, message: OutboxMessage) -> None:
        try:
            self.dispatcher.dispatch(message=message)

            async with self.uow as uow:
                await uow.outbox_repo.mark_published(id=message.id)

        except Exception:
            async with self.uow as uow:
                await uow.outbox_repo.mark_failed(id=message.id)
                await uow.commit()
