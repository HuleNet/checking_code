from typing import Any


class BaseError(Exception):
    code: str = "base_error"

    def __init__(
        self,
        message: str,
        *,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.details = details or {}


class DomainError(BaseError):
    code = "base_domain_error"


class InvariantViolationError(DomainError):
    code = "invariant_violation"
