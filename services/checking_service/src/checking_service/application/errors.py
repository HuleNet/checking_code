from checking_service.domain.errors import BaseError


class ApplicationError(BaseError):
    code = "base_application_error"


class ValidationError(ApplicationError):
    code = "validation_error"


class NotFoundError(ApplicationError):
    code = "not_found"


class ServiceExecutionError(ApplicationError):
    code = "service_execution_error"


class RunnerError(ServiceExecutionError):
    code = "runner_error"


class RunnerContractViolationError(ServiceExecutionError):
    code = "runner_contract_violation"


class JudgeError(ServiceExecutionError):
    code = "judge_error"


class JudgeCompareError(JudgeError):
    code = "judge_compare_error"


class InternalServiceError(ApplicationError):
    code = "internal_service_error"
