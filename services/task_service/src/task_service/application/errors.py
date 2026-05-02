from task_service.domain.errors import BaseError


class ApplicationError(BaseError):
    code = "base_application_error"


class ValidationError(ApplicationError):
    code = "validation_error"


class NotFoundError(ApplicationError):
    code = "not_found"


class InternalError(ApplicationError):
    code = "internal_error"
