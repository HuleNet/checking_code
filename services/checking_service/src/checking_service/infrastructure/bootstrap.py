from functools import cached_property

from checking_service.application.services import EvaluationService, JudgeService
from checking_service.application.use_cases.evaluation import RunEvaluationUseCase
from checking_service.infrastructure.db.session import SessionLocal
from checking_service.infrastructure.db import SQLAlchemyUnitOfWork
from checking_service.infrastructure.runners import DockerRunner
from checking_service.infrastructure.core import get_settings_cached


class Container:
    @cached_property
    def settings(self):
        return get_settings_cached()

    @cached_property
    def uow(self) -> SQLAlchemyUnitOfWork:
        return SQLAlchemyUnitOfWork(session_factory=SessionLocal)

    @cached_property
    def runner(self) -> DockerRunner:
        return DockerRunner(
            timeout_sec=self.settings.time_limit_sec,
            memory_limit_mb=self.settings.memory_limit_mb,
            cpu_limit=self.settings.run_cpu_limit,
        )

    @cached_property
    def judge_service(self) -> JudgeService:
        return JudgeService(epsilon=self.settings.epsilon)

    @cached_property
    def evaluation_service(self) -> EvaluationService:
        return EvaluationService(
            runner=self.runner,
            judge=self.judge_service,
            max_stdio_length=self.settings.max_stdio_length,
        )

    def run_evaluation_use_case(self) -> RunEvaluationUseCase:
        return RunEvaluationUseCase(
            uow=self.uow,
            evaluation_service=self.evaluation_service,
            stuck_time_sec=self.settings.stuck_time_sec,
        )


container = Container()
