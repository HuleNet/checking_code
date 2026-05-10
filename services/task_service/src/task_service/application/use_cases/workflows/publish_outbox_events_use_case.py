from uuid import UUID

from task_service.application.ports import UnitOfWork, TaskDispatcher
from task_service.application.errors import InternalError


class PublishOutboxEventsUseCase:
    def __init__(self, uow: UnitOfWork, task_dispatcher: TaskDispatcher) -> None:
        self.uow = uow
        self.task_dispatcher = task_dispatcher

    async def execute(self, batch_size: int = 100) -> None:
        try:
            async with self.uow as uow:
                messages = await uow.outbox_repo.get_unprocessed(limit=batch_size)

                if not messages:
                    return

                for message in messages:
                    if message.event_type == "SubmissionCreatedEvent":
                        await self.task_dispatcher.process_submission(
                            submission_id=UUID(message.payload["submission_id"])
                        )

                await uow.outbox_repo.mark_processed(
                    ids=[message.id for message in messages]
                )
                await uow.commit()

        except Exception as exc:
            raise InternalError(
                message="Failed to publish OutboxEvents",
                details={
                    "entity": "OutboxEvent",
                },
            ) from exc
