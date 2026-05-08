from asyncio import run
from uuid import UUID

from celery import shared_task
from httpx import HTTPError, TimeoutException

from task_service.infrastructure.bootstrap import container


@shared_task(
    name="process_submission",
    autoretry_for=(HTTPError, TimeoutException),
    retry_backoff=True,
    retry_backoff_max=300,
    retry_jitter=True,
    max_retries=5,
    acks_late=True,
)
def process_submission(submission_id: str) -> None:
    run(
        container.use_cases.process_submission.execute(
            submission_id=UUID(submission_id)
        )
    )


@shared_task(
    name="poll_submission_result",
    autoretry_for=(HTTPError, TimeoutException),
    retry_backoff=True,
    retry_backoff_max=300,
    retry_jitter=True,
    max_retries=20,
    acks_late=True,
)
def poll_submission_result(
    submission_id: str,
    evaluation_id: str,
) -> None:
    run(
        container.use_cases.poll_submission_result.execute(
            submission_id=UUID(submission_id),
            evaluation_id=UUID(evaluation_id),
        )
    )
