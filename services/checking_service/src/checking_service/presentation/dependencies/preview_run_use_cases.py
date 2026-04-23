from checking_service.application.use_cases.preview_run import PreviewRunUseCase
from checking_service.infrastructure.bootstrap import container


def get_use_case_preview_run() -> PreviewRunUseCase:
    return PreviewRunUseCase(
        uow=container.uow, evaluation_service=container.evaluation_service
    )
