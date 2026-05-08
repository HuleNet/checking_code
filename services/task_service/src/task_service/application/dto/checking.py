from dataclasses import dataclass


@dataclass(frozen=True)
class CheckingResultDTO:
    tests_passed: int
    tests_total: int


@dataclass(frozen=True)
class PreviewRunDTO:
    assignment_id: str
    language: str
    code: str
