from task_service.domain.errors import BaseError


class ApplicationError(BaseError):
    code = "base_application_error"


class ValidationError(ApplicationError):
    code = "validation_error"


class NotFoundError(ApplicationError):
    code = "not_found"


class SubmissionAttemptError(ApplicationError):
    code = "submission_attempt_error"


class InternalError(ApplicationError):
    code = "internal_error"
