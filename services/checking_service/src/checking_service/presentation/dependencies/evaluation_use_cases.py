from checking_service.application.use_cases.evaluation import (
    StartEvaluationUseCase,
    GetEvaluationUseCase,
    GetEvaluationsBySubmissionUseCase,
    GetEvaluationPageUseCase,
    DeleteEvaluationUseCase,
)
from checking_service.infrastructure.bootstrap import container


def get_use_case_start_evaluation() -> StartEvaluationUseCase:
    return StartEvaluationUseCase(uow=container.uow)


def get_use_case_get_evaluation() -> GetEvaluationUseCase:
    return GetEvaluationUseCase(uow=container.uow)


def get_use_case_get_by_submission_evaluations() -> GetEvaluationsBySubmissionUseCase:
    return GetEvaluationsBySubmissionUseCase(uow=container.uow)


def get_use_case_get_evaluation_page() -> GetEvaluationPageUseCase:
    return GetEvaluationPageUseCase(uow=container.uow)


def get_use_case_delete_evaluation() -> DeleteEvaluationUseCase:
    return DeleteEvaluationUseCase(uow=container.uow)
