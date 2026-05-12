from logging import getLogger
from uuid import UUID

from checking_service.application.dto.submission import SubmissionDTO
from checking_service.infrastructure.broker import broker
from checking_service.infrastructure.bootstrap import container


logger = getLogger(__name__)


@broker.task(task_name="run_evaluation", labels={"routing_key": "checking_queue"})
async def run_evaluation_task(
    submission_id: str, assignment_id: str, code: str, language: str
) -> None:
    try:
        dto = SubmissionDTO(
            id=UUID(submission_id),
            assignment_id=UUID(assignment_id),
            language=language,
            code=code,
        )
        await container.use_cases.run_evaluation.execute(dto=dto)
        logger.info(
            "Evaluation completed",
            extra={
                "submission_id": submission_id,
                "assignment_id": assignment_id,
            },
        )

    except Exception:
        logger.exception(
            "Failed to run evaluation",
            extra={
                "submission_id": submission_id,
                "assignment_id": assignment_id,
            },
        )
        raise
