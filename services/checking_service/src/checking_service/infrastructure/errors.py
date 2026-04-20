from checking_service.domain.errors import BaseError


class RepositoryError(BaseError):
    code = "repository_error"


class RepositoryIntegrityError(RepositoryError):
    code = "repository_integrity_error"


class InternalRepositoryError(RepositoryError):
    code = "internal_repository_error"
