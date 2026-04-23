from checking_service.application.use_cases.execution_case import (
    GetExecutionCaseUseCase,
    GetExecutionCasesByEvaluationUseCase,
    GetExecutionCasePageUseCase,
)
from checking_service.infrastructure.bootstrap import container


def get_use_case_get_execution_case() -> GetExecutionCaseUseCase:
    return GetExecutionCaseUseCase(uow=container.uow)


def get_use_case_get_by_evaluation_execution_cases() -> (
    GetExecutionCasesByEvaluationUseCase
):
    return GetExecutionCasesByEvaluationUseCase(uow=container.uow)


def get_use_case_get_execution_case_page() -> GetExecutionCasePageUseCase:
    return GetExecutionCasePageUseCase(uow=container.uow)
