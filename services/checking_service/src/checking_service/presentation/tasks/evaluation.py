from asyncio import run
from logging import getLogger
from dataclasses import asdict
from uuid import UUID

from celery.exceptions import SoftTimeLimitExceeded

from checking_service.application.dto.submission import SubmissionDTO
from checking_service.infrastructure.broker import celery_app
from checking_service.infrastructure.bootstrap import container


logger = getLogger(__name__)


@celery_app.task(
    name="run_evaluation",
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_backoff_max=60,
    retry_jitter=True,
    max_retries=3,
    acks_late=True,
)
def run_evaluation(
    submission_id: str, assignment_id: str, code: str, language: str
) -> dict:
    try:
        dto = SubmissionDTO(
            id=UUID(submission_id),
            assignment_id=UUID(assignment_id),
            language=language,
            code=code,
        )
        result = run(container.use_cases.run_evaluation.execute(dto=dto))
        logger.info(
            "Evaluation completed",
            extra={
                "submission_id": submission_id,
                "assignment_id": assignment_id,
            },
        )
        return asdict(result)

    except SoftTimeLimitExceeded:
        logger.warning(
            "Evaluation soft timeout exceeded",
            extra={
                "submission_id": submission_id,
            },
        )
        raise

    except Exception:
        logger.exception(
            "Failed to run evaluation",
            extra={
                "submission_id": submission_id,
                "assignment_id": assignment_id,
            },
        )
        raise
