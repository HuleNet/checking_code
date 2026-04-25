from checking_service.domain.errors import BaseError


class TransientError(Exception):
    pass


class PermanentError(Exception):
    pass


class InfrastructureError(BaseError):
    code = "infrastructure_error"


class RepositoryError(InfrastructureError, PermanentError):
    code = "repository_error"


class RepositoryIntegrityError(RepositoryError):
    code = "repository_integrity_error"


class RepositoryInternalError(RepositoryError):
    code = "repository_internal_error"


class RunnerError(InfrastructureError, TransientError):
    code = "runner_error"
