from asyncio import sleep, run

from checking_service.application.models.outbox import OutboxMessage
from checking_service.application.ports import UnitOfWork
from checking_service.infrastructure.messaging import CeleryDispatcher
from checking_service.infrastructure.bootstrap import container


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
                await uow.commit()

        except Exception:
            async with self.uow as uow:
                await uow.outbox_repo.mark_failed(id=message.id)
                await uow.commit()


async def main() -> None:
    uow = container.uow
    dispatcher = CeleryDispatcher()
    publisher = OutboxPublisher(
        uow=uow,
        dispatcher=dispatcher,
        batch_size=10,
    )
    await publisher.run_forever()
    
    
if __name__ =="__main__":
    run(main())    
