from checking_service.domain.errors import BaseError


class InfrastructureError(BaseError):
    code = "infrastructure_error"


class RepositoryError(InfrastructureError):
    code = "repository_error"


class RepositoryIntegrityError(RepositoryError):
    code = "repository_integrity_error"


class RepositoryInternalError(RepositoryError):
    code = "repository_internal_error"


class RunnerError(InfrastructureError):
    code = "runner_error"
