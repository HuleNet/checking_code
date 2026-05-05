from task_service.domain.errors import BaseError


class InfrastructureError(BaseError):
    code = "infrastructure_error"
