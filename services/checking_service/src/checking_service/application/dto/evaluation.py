from dataclasses import dataclass
from uuid import UUID
from datetime import datetime

from checking_service.application.dto.execution_case import ExecutionCaseDTO


@dataclass(frozen=True)
class EvaluationDTO:
    id: UUID
    submission_id: UUID
    total_tests_count: int
    passed_tests_count: int
    status: str
    created_at: datetime
    started_at: datetime | None


@dataclass(frozen=True)
class CreateEvaluationDTO:
    submission_id: UUID
    total_tests_count: int


@dataclass(frozen=True)
class PreviewEvaluationDTO:
    total_tests_count: int
    passed_tests_count: int
    status: str
    summary_execution_case: ExecutionCaseDTO | None
