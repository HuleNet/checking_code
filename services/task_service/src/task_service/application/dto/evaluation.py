from dataclasses import dataclass
from typing import Literal


EvaluationStatus = Literal[
    "PENDING",
    "RUNNING",
    "PASSED",
    "FAILED",
    "ERROR",
]


@dataclass(frozen=True)
class EvaluationDTO:
    id: str
    status: EvaluationStatus
    tests_passed: int | None = None
    tests_total: int | None = None
