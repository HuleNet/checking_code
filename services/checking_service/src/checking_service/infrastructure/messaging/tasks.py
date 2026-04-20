from asyncio import run

from checking_service.application.models.outbox import RunEvaluationRequested
from checking_service.infrastructure.core import celery_app
from checking_service.infrastructure.bootstrap import build_run_evaluation_use_case


@celery_app.task(name="run_evaluation")
def run_evaluation(**payload):
    use_case = build_run_evaluation_use_case()
    event = RunEvaluationRequested(
        evaluation_id=payload["evaluation_id"],
        submission_id=payload["submission_id"],
        assignment_id=payload["assignment_id"],
        language=payload["language"],
        code=payload["code"],
    )
    run(use_case.execute(event=event))
