from uuid import UUID

from celery import Celery

from task_service.application.ports import TaskDispatcher


class CeleryTaskDispatcher(TaskDispatcher):
    def __init__(
        self,
        celery_app: Celery,
    ) -> None:
        self.celery_app = celery_app

    async def process_submission(
        self,
        submission_id: UUID,
    ) -> None:
        self.celery_app.send_task(
            "process_submission",
            kwargs={
                "submission_id": str(submission_id),
            },
        )

    async def finalize_group_assignment(
        self,
        group_assignment_id: UUID,
    ) -> None:
        self.celery_app.send_task(
            "finalize_group_assignment",
            kwargs={
                "group_assignment_id": str(group_assignment_id),
            },
        )
