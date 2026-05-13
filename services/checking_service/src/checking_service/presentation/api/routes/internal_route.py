from fastapi import APIRouter, status

from checking_service.presentation.schemas.evaluation import StartEvaluationRequest
from checking_service.presentation.tasks import run_evaluation_task


internal_router = APIRouter(prefix="/internal/evaluations", tags=["Internal"])


@internal_router.post(
    "/run",
    status_code=status.HTTP_202_ACCEPTED,
)
async def run_evaluation(payload: StartEvaluationRequest) -> None:
    await (
        run_evaluation_task.kicker()
        .with_labels(routing_key="checking_queue")
        .kiq(
            submission_id=str(payload.submission_id),
            assignment_id=str(payload.assignment_id),
            code=payload.code,
            language=payload.language,
        )
    )
