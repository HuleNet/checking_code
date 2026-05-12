from logging import getLogger
from uuid import UUID

from task_service.application.dto.submission import ApplySubmissionResultDTO
from task_service.infrastructure.broker import broker
from task_service.infrastructure.bootstrap import container


logger = getLogger(__name__)


@broker.task(task_name="apply_submission_result_task", labels={"routing_key": "task_queue"})
async def apply_submission_result_task(
    id: str, submission_id: str, tests_total: int, tests_passed: int
) -> None:
    try:
        dto = ApplySubmissionResultDTO(
            id=UUID(submission_id),
            evaluation_id=UUID(id),
            tests_total=tests_total,
            tests_passed=tests_passed,
        )
        await container.use_cases.apply_submission_result.execute(dto)

    except Exception:
        logger.exception(
            "Failed to process submission",
            extra={
                "submission_id": submission_id,
            },
        )
        raise


@broker.task(
    task_name="scan_expired_group_assignments_task",
    schedule=[{"cron": "*/1 * * * *"}],
    labels={"routing_key": "task_queue"},
)
async def scan_expired_group_assignments_task() -> None:
    try:
        await container.use_cases.scan_expired_group_assignments.execute()

    except Exception:
        logger.exception(
            "Failed to scan expired group assignments",
        )
        raise
