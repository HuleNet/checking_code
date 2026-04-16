from dataclasses import dataclass
from uuid import UUID

from checking_service.domain.enums import Language
from checking_service.domain.errors import InvariantViolationError


@dataclass(frozen=True)
class Submission:
    id: UUID
    assignment_id: UUID
    language: Language
    code: str

    def __post_init__(self) -> None:
        self._check_invariants()

    def _check_invariants(self) -> None:
        if not self.code.strip():
            raise InvariantViolationError(
                message="Code must not be empty",
                details={
                    "code": self.code,
                },
            )
