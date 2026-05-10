from dataclasses import dataclass
from uuid import UUID

from checking_service.domain.value_objects import CheckType
from checking_service.domain.errors import InvariantViolationError


@dataclass(frozen=True)
class TestCase:
    id: UUID
    assignment_id: UUID
    input_data: str
    expected_output: str
    check_type: CheckType

    def __post_init__(self) -> None:
        self._check_invariants()

    def _check_invariants(self) -> None:
        if not self.input_data and not self.expected_output:
            raise InvariantViolationError(
                message="Input data or expected output must not be empty",
                details={
                    "entity": "test_case",
                    "input_data": self.input_data,
                    "expected_output": self.expected_output,
                },
            )
