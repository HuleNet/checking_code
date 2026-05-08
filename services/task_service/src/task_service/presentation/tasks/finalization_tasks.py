from asyncio import run
from uuid import UUID
from datetime import datetime, timezone

from celery import shared_task

from task_service.domain.services import ScoringService
from task_service.application.use_cases.final_result import CreateFinalResultsUseCase
from task_service.infrastructure.db import SQLAlchemyUnitOfWork, SessionLocal
from task_service.infrastructure.broker.celery_app import celery_app
from task_service.infrastructure.core import get_settings_cached


settings = get_settings_cached()


async def _finalize_group_assignment(
    group_assignment_id: str,
) -> None:
    uow = SQLAlchemyUnitOfWork(session_factory=SessionLocal)
    create_final_results_use_case = CreateFinalResultsUseCase(
        uow=uow,
        scoring_service=ScoringService(
            max_attempts=settings.max_attempts, penalty_cap=settings.penalty_cap
        ),
    )
    await create_final_results_use_case.execute(
        group_assignment_id=UUID(group_assignment_id)
    )

    async with uow:
        await uow.group_assignment_repo.finalize(id=UUID(group_assignment_id))
        await uow.commit()


async def _scan_expired_group_assignments(
    limit: int = 100,
) -> None:
    uow = SQLAlchemyUnitOfWork(session_factory=SessionLocal)

    async with uow:
        expired_group_assignments = await uow.group_assignment_repo.claim_expired(
            now=datetime.now(timezone.utc), limit=limit
        )
        await uow.commit()

    for group_assignment in expired_group_assignments:
        celery_app.send_task(
            "finalize_group_assignment",
            kwargs={"group_assignment_id": str(group_assignment.id)},
        )


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
    run(_finalize_group_assignment(group_assignment_id=group_assignment_id))


@shared_task(
    name="scan_expired_group_assignments",
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_backoff_max=60,
    retry_jitter=True,
    max_retries=10,
    acks_late=True,
)
def scan_expired_group_assignments() -> None:
    run(_scan_expired_group_assignments())
