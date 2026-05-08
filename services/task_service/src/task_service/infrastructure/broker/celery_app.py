from celery import Celery

from task_service.infrastructure.core import get_settings_cached


celery_app = Celery(
    "task_service",
    broker=get_settings_cached().broker_url,
    backend=None,
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
        "process_submission": {
            "queue": "submission.check",
        },
        "poll_submission_result": {"queue": "submission.check"},
        "finalize_group_assignment": {
            "queue": "group_assignment.finalize",
        },
        "scan_expired_group_assignments": {
            "queue": "group_assignment.finalize",
        },
        "publish_outbox_events": {
            "queue": "outbox.publish",
        },
    },
    beat_schedule={
        "publish-outbox-events": {
            "task": "publish_outbox_events",
            "schedule": 5.0,
        },
        "finalize-expired-group-assignments": {
            "task": "scan_expired_group_assignments",
            "schedule": 30.0,
        },
    },
)
celery_app.autodiscover_tasks(
    [
        "task_service.presentation.tasks",
    ]
)
