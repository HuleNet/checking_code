from checking_service.domain.errors import BaseError


class DatabaseError(BaseError):
    code = "database_error"
