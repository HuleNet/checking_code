from asyncio import run
from uuid import UUID

from celery import shared_task

from checking_service.infrastructure.bootstrap import container


@shared_task(
    name="run_evaluation",
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_backoff_max=300,
    retry_jitter=True,
    max_retries=5,
    acks_late=True,
)
def run_evaluation(evaluation_id: str, code: str, language: str) -> None:
    run(
        container.use_cases.run_evaluation.execute(
            evaluation_id=UUID(evaluation_id),
            code=code,
            language=language,
        )
    )
