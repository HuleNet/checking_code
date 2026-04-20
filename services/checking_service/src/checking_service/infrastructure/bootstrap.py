from checking_service.application.services import EvaluationService, JudgeService
from checking_service.application.use_cases.evaluation import RunEvaluationUseCase
from checking_service.infrastructure.db.session import SessionLocal
from checking_service.infrastructure.db import SQLAlchemyUnitOfWork
from checking_service.infrastructure.runners import DockerRunner
from checking_service.infrastructure.core import get_settings_cached


def build_run_evaluation_use_case() -> RunEvaluationUseCase:
    sessionLocal = SessionLocal
    uow = SQLAlchemyUnitOfWork(session_factory=sessionLocal)
    runner = DockerRunner(
        timeout_sec=get_settings_cached().time_limit_sec,
        memory_limit_mb=get_settings_cached().memory_limit_mb,
        cpu_limit=get_settings_cached().run_cpu_limit,
    )
    judge = JudgeService(epsilon=get_settings_cached().epsilon)
    evaluation_service = EvaluationService(
        runner=runner,
        judge=judge,
        max_stdio_length=get_settings_cached().max_stdio_length,
    )
    return RunEvaluationUseCase(
        uow=uow,
        evaluation_service=evaluation_service,
        stuck_time_sec=get_settings_cached().stuck_time_sec,
    )
