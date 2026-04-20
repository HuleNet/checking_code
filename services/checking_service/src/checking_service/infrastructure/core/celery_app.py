from celery import Celery

from checking_service.infrastructure.core import get_settings_cached


EVALUATION_QUEUE = "run_evaluation"


celery_app = Celery(
    "checking_service",
    broker=get_settings_cached().broker_url,
)
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    task_default_queue=EVALUATION_QUEUE,
    task_routes={
        "run_evaluation": {
            "queue": EVALUATION_QUEUE,
        }
    },
)
