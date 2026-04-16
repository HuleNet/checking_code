from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class InputCaseDTO:
    id: UUID
    assignment_id: UUID
    input_data: str
    expected_output: str
    check_type: str


@dataclass(frozen=True)
class CreateInputCaseDTO:
    assignment_id: UUID
    input_data: str
    expected_output: str
    check_type: str


@dataclass(frozen=True)
class UpdateInputCaseDTO:
    input_data: str | None = None
    expected_output: str | None = None
    check_type: str | None = None
