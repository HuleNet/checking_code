from dataclasses import dataclass
from uuid import UUID
from datetime import datetime


@dataclass
class EvaluationDTO:
    id: UUID
    submission_id: UUID
    total_tests_count: int
    status: str
    passed_tests: int
    failed_tests: int
    error_tests: int
    created_at: datetime


@dataclass
class CreateEvaluationDTO:
    submission_id: UUID
    total_tests_count: int
