from dataclasses import dataclass
from uuid import UUID
from datetime import datetime


@dataclass(frozen=True)
class EvaluationDTO:
    id: UUID
    submission_id: UUID
    tests_total: int
    tests_passed: int
    status: str
    created_at: datetime


@dataclass(frozen=True)
class PreviewEvaluationDTO:
    tests_total: int
    tests_passed: int
    status: str
