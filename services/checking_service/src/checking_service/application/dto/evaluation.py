from dataclasses import dataclass
from uuid import UUID
from datetime import datetime


@dataclass
class EvaluationDTO:
    id: UUID
    submission_id: UUID
    total_tests_count: int
    passed_tests_count: int
    status: str
    created_at: datetime


@dataclass
class CreateEvaluationDTO:
    submission_id: UUID
    total_tests_count: int
