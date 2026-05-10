from celery import Celery

from checking_service.application.ports import TaskDispatcher


class CeleryTaskDispatcher(TaskDispatcher):
    def __init__(self, celery_app: Celery) -> None:
        self.celery_app = celery_app

    async def dispatch(self, task_name: str, payload: dict):
        self.celery_app.send_task(
            name=task_name,
            kwargs={"payload": payload},
        )
