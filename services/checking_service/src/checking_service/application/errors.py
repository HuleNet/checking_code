from checking_service.domain.errors import BaseError


class ApplicationError(BaseError):
    code = "base_application_error"


class ValidationError(ApplicationError):
    code = "validation_error"


class NotFoundError(ApplicationError):
    code = "not_found"


class InternalError(ApplicationError):
    code = "internal_error"


class RunnerError(BaseError):
    code = "runner_error"


class RunnerMemoryError(RunnerError):
    code = "runner_memory_error"


class RunnerExecutionError(RunnerError):
    code = "runner_execution_error"
