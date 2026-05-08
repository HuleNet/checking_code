from asyncio import run
from uuid import UUID

from celery import shared_task

from task_service.infrastructure.bootstrap import container


@shared_task(
    name="finalize_group_assignment",
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_backoff_max=300,
    retry_jitter=True,
    max_retries=5,
    acks_late=True,
)
def finalize_group_assignment(group_assignment_id: str) -> None:
    run(
        container.use_cases.finalize_group_assignment.execute(
            group_assignment_id=UUID(group_assignment_id)
        )
    )


@shared_task(
    name="scan_expired_group_assignments",
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_jitter=True,
    max_retries=10,
)
def scan_expired_group_assignments() -> None:
    run(container.use_cases.scan_expired_group_assignments.execute())
