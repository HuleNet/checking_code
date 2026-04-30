from task_service.domain.errors import BaseError


class ApplicationError(BaseError):
    code = "base_application_error"
