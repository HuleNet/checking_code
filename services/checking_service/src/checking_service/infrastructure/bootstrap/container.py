from functools import cached_property

from checking_service.domain.services import JudgeService
from checking_service.infrastructure.db import SQLAlchemyUnitOfWork, SessionLocal
from checking_service.infrastructure.broker import celery_app, CeleryTaskDispatcher
from checking_service.infrastructure.runners import DockerRunner
from checking_service.infrastructure.core import get_settings_cached
from checking_service.infrastructure.bootstrap.use_cases import UseCases


class Container:
    @cached_property
    def settings(self):
        return get_settings_cached()

    @cached_property
    def judge_service(self) -> JudgeService:
        return JudgeService(epsilon=self.settings.epsilon)

    @cached_property
    def runner(self) -> DockerRunner:
        return DockerRunner(
            timeout_sec=self.settings.time_limit_sec,
            memory_limit_mb=self.settings.memory_limit_mb,
            cpu_limit=self.settings.run_cpu_limit,
        )

    @cached_property
    def task_dispatcher(self) -> CeleryTaskDispatcher:
        return CeleryTaskDispatcher(celery_app=celery_app)

    def uow(self) -> SQLAlchemyUnitOfWork:
        return SQLAlchemyUnitOfWork(session_factory=SessionLocal)

    @cached_property
    def use_cases(self) -> UseCases:
        return UseCases(
            uow_factory=self.uow,
            judge_service=self.judge_service,
            runner=self.runner,
            task_dispatcher=self.task_dispatcher,
            settings=self.settings,
        )


container = Container()
