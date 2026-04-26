from logging import getLogger
from asyncio import sleep, run

from checking_service.application.models.outbox import OutboxMessage
from checking_service.application.ports import UnitOfWork
from checking_service.infrastructure.messaging import CeleryDispatcher
from checking_service.infrastructure.errors import TransientError, PermanentError
from checking_service.infrastructure.bootstrap import container
from checking_service.infrastructure.core import get_settings_cached, setup_logging


logger = getLogger(__name__)


class OutboxPublisher:
    def __init__(
        self, uow: UnitOfWork, dispatcher: CeleryDispatcher, batch_size: int
    ) -> None:
        self.uow = uow
        self.dispatcher = dispatcher
        self.batch_size = batch_size

    async def run_forever(self) -> None:
        logger.info("outbox_publisher_started")

        while True:
            await self._process_batch()
            await sleep(1)

    async def _process_batch(self) -> None:
        async with self.uow as uow:
            messages = await uow.outbox_repo.claim_batch(self.batch_size)
            await uow.commit()

        if not messages:
            return

        logger.info(
            "outbox_batch_claimed",
            extra={
                "extra": {
                    "batch_size": len(messages),
                },
            },
        )

        for message in messages:
            await self._handle_message(message=message)

    async def _handle_message(self, message: OutboxMessage) -> None:
        try:
            await self.dispatcher.dispatch(message=message)

            async with self.uow as uow:
                await uow.outbox_repo.mark_published(id=message.id)
                await uow.commit()
                logger.info(
                    "outbox_messages_published",
                    extra={
                        "extra": {
                            "message_id": str(message.id),
                            "event_type": message.event_type,
                        },
                    },
                )

        except TransientError as exc:
            logger.warning(
                "outbox_message_transient_error",
                extra={
                    "extra": {
                        "message_id": str(message.id),
                        "event_type": message.event_type,
                        "error": repr(exc),
                    },
                },
            )
            async with self.uow as uow:
                await uow.outbox_repo.mark_failed(id=message.id)
                await uow.commit()

        except PermanentError as exc:
            logger.error(
                "outbox_message_permanent_error",
                extra={
                    "extra": {
                        "message_id": str(message.id),
                        "event_type": message.event_type,
                        "error": repr(exc),
                    },
                },
            )
            async with self.uow as uow:
                await uow.outbox_repo.mark_failed_permanently(id=message.id)
                await uow.commit()

        except Exception as exc:
            logger.exception(
                "outbox_message_unexpected_error",
                extra={
                    "extra": {
                        "message_id": str(message.id),
                        "event_type": message.event_type,
                        "error": repr(exc),
                    },
                },
            )
            async with self.uow as uow:
                await uow.outbox_repo.mark_failed(id=message.id)
                await uow.commit()


async def main() -> None:
    setup_logging()
    logger.info("outbox_publisher_bootstrap")
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
