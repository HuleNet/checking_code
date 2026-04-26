from asyncio import run

from checking_service.application.dto.mappers import DomainEnumsMapper
from checking_service.application.models.outbox import RunEvaluationRequested
from checking_service.infrastructure.core import celery_app
from checking_service.infrastructure.errors import TransientError, PermanentError
from checking_service.infrastructure.bootstrap import container


@celery_app.task(
    name="RUN_EVALUATION_REQUESTED",
    bind=True,
    autoretry_for=(TransientError,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 1},
)
def run_evaluation(self, **payload):
    try:
        use_case = container.run_evaluation_use_case()
        event = RunEvaluationRequested(
            evaluation_id=payload["evaluation_id"],
            submission_id=payload["submission_id"],
            assignment_id=payload["assignment_id"],
            language=DomainEnumsMapper.map_language(payload["language"]),
            code=payload["code"],
        )
        run(use_case.execute(event=event))

    except PermanentError:
        raise
