from checking_service.application.use_cases.input_case import (
    CreateInputCaseUseCase,
    GetInputCaseUseCase,
    GetInputCasesByAssignmentUseCase,
    GetInputCasePageUseCase,
    UpdateInputCaseUseCase,
    DeleteInputCaseUseCase,
)
from checking_service.infrastructure.bootstrap import container


def get_use_case_create_input_case() -> CreateInputCaseUseCase:
    return CreateInputCaseUseCase(uow=container.uow)


def get_use_case_get_input_case() -> GetInputCaseUseCase:
    return GetInputCaseUseCase(uow=container.uow)


def get_use_case_get_by_assignment_input_case() -> GetInputCasesByAssignmentUseCase:
    return GetInputCasesByAssignmentUseCase(uow=container.uow)


def get_use_case_get_input_case_page() -> GetInputCasePageUseCase:
    return GetInputCasePageUseCase(uow=container.uow)


def get_ues_case_update_input_case() -> UpdateInputCaseUseCase:
    return UpdateInputCaseUseCase(uow=container.uow)


def get_use_case_delete_input_case() -> DeleteInputCaseUseCase:
    return DeleteInputCaseUseCase(uow=container.uow)
