from celery import Celery

from checking_service.infrastructure.core import get_settings_cached


celery_app = Celery(
    "checking_service",
    broker=get_settings_cached().broker_url,
)
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    worker_prefetch_multiplier=1,
    task_soft_time_limit=10,
    task_time_limit=15,
    task_routes={
        "run_evaluation": {
            "queue": "checking.evaluation.evaluate",
        },
    },
    task_track_started=True,
    worker_max_tasks_per_child=100,
)
celery_app.autodiscover_tasks(
    [
        "checking_service.presentation.tasks",
    ]
)
