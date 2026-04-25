from asyncio import sleep, run

from checking_service.application.models.outbox import OutboxMessage
from checking_service.application.ports import UnitOfWork
from checking_service.infrastructure.messaging import CeleryDispatcher
from checking_service.infrastructure.errors import TransientError, PermanentError
from checking_service.infrastructure.bootstrap import container
from checking_service.infrastructure.core import get_settings_cached


class OutboxPublisher:
    def __init__(
        self, uow: UnitOfWork, dispatcher: CeleryDispatcher, batch_size: int
    ) -> None:
        self.uow = uow
        self.dispatcher = dispatcher
        self.batch_size = batch_size

    async def run_forever(self) -> None:
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
            await self.dispatcher.dispatch(message=message)

            async with self.uow as uow:
                await uow.outbox_repo.mark_published(id=message.id)
                await uow.commit()

        # exc для logger
        except TransientError as exc:
            async with self.uow as uow:
                await uow.outbox_repo.mark_failed(id=message.id)
                await uow.commit()

        # exc для logger
        except PermanentError as exc:
            async with self.uow as uow:
                await uow.outbox_repo.mark_failed_permanently(id=message.id)
                await uow.commit()

        # exc для logger
        except Exception as exc:
            async with self.uow as uow:
                await uow.outbox_repo.mark_failed(id=message.id)
                await uow.commit()


async def main() -> None:
    uow = container.uow
    dispatcher = CeleryDispatcher()
    publisher = OutboxPublisher(
        uow=uow,
        dispatcher=dispatcher,
        batch_size=get_settings_cached().outbox_batch_size,
    )
    await publisher.run_forever()


if __name__ == "__main__":
    run(main())
