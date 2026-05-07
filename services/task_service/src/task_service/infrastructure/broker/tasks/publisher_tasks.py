from asyncio import run

from celery import shared_task

from task_service.infrastructure.db import SQLAlchemyUnitOfWork, SessionLocal
from task_service.infrastructure.broker.celery_app import celery_app


EVENT_TASK_MAP = {
    "SubmissionCreatedEvent": "process_submission",
}


async def _publish_outbox_events(batch_size: int = 100) -> None:
    async with SQLAlchemyUnitOfWork(session_factory=SessionLocal) as uow:
        messages = await uow.outbox_repo.get_unprocessed(limit=batch_size)

        for message in messages:
            task_name = EVENT_TASK_MAP.get(message.event_type)

            if task_name is None:
                continue

            if message.event_type == "SubmissionCreatedEvent":
                celery_app.send_task(
                    task_name,
                    kwargs={
                        "submission_id": message.payload["submission_id"],
                    },
                )

            await uow.outbox_repo.mark_processed(id=message.id)

        await uow.commit()


@shared_task(
    name="publish_outbox_events",
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_backoff_max=60,
    retry_jitter=True,
    max_retries=10,
    acks_late=True,
)
def publish_outbox_events() -> None:
    run(_publish_outbox_events())
