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
    task_routes={
        "run_evaluation": {
            "queue": "checking.evaluation.evaluate",
        },
        "publish_outbox_events": {
            "queue": "checking.outbox.publish",
        },
    },
    beat_schedule={
        "publish-outbox-events": {
            "task": "publish_outbox_events",
            "schedule": 5.0,
        },
    },
)
celery_app.autodiscover_tasks(
    [
        "checking_service.presentation.tasks",
    ]
)
