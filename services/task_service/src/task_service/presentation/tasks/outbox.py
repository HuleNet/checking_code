from asyncio import run

from celery import shared_task

from task_service.infrastructure.bootstrap import container


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
    run(container.use_cases.publish_outbox_events.execute())
