from uuid import UUID
from asyncio import run

from httpx import AsyncClient, Timeout, TimeoutException, HTTPError
from celery import shared_task

from task_service.application.dto.submission import ApplySubmissionResultDTO
from task_service.application.use_cases.submission import (
    GetSubmissionUseCase,
    StartSubmissionProcessingUseCase,
    ApplySubmissionResultUseCase,
    FailSubmissionUseCase,
)
from task_service.infrastructure.db import SQLAlchemyUnitOfWork, SessionLocal
from task_service.infrastructure.core import get_settings_cached


settings = get_settings_cached()


async def _process_submission(submission_id: str) -> None:
    submission_uuid = UUID(submission_id)
    uow = SQLAlchemyUnitOfWork(session_factory=SessionLocal)
    get_submission_use_case = GetSubmissionUseCase(uow=uow)
    start_submission_use_case = StartSubmissionProcessingUseCase(uow=uow)
    apply_result_use_case = ApplySubmissionResultUseCase(uow=uow)
    fail_submission_use_case = FailSubmissionUseCase(uow=uow)
    submission = await get_submission_use_case.execute(id=submission_uuid)

    if submission.status != "PENDING":
        return

    await start_submission_use_case.execute(id=submission.id)

    try:
        async with AsyncClient(timeout=Timeout(30.0)) as client:
            response = await client.post(
                f"{settings.checking_service_url}/evaluations/start",
                json={
                    "submission_id": str(submission.id),
                    "assignment_id": str(submission.assignment_id),
                    "language": submission.language,
                    "code": submission.code,
                },
            )
            response.raise_for_status()
            payload = response.json()

    except Exception:
        await fail_submission_use_case.execute(id=submission.id)
        raise

    try:
        async with AsyncClient(timeout=Timeout(30.0)) as client:
            response = await client.get(
                f"{settings.checking_service_url}/evaluations/{payload['id']}",
                params=payload["id"],
            )
            response.raise_for_status()
            payload = response.json()

    except Exception:
        await fail_submission_use_case.execute(id=submission.id)
        raise

    await apply_result_use_case.execute(
        dto=ApplySubmissionResultDTO(
            id=submission.id,
            tests_passed=payload["passed_tests_count"],
            tests_total=payload["total_tests_count"],
        ),
    )


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
    run(_process_submission(submission_id=submission_id))
