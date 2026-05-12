from fastapi import APIRouter, status

from task_service.presentation.schemas.evaluation import EvaluationResultRequest
from task_service.presentation.tasks import apply_submission_result_task


internal_router = APIRouter(prefix="/internal/submissions", tags=["Internal"])


@internal_router.post(
    "/complete",
    status_code=status.HTTP_202_ACCEPTED,
)
async def complete_submission(payload: EvaluationResultRequest) -> None:
    await apply_submission_result_task.kicker().with_labels(
        routing_key="task_queue"
    ).kiq(
        id=str(payload.id),
        submission_id=str(payload.submission_id),
        tests_total=payload.tests_total,
        tests_passed=payload.tests_passed,
    )
