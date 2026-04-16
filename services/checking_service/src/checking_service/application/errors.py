from checking_service.domain.errors import BaseError


class ValidationError(BaseError):
    code = "validation_error"
