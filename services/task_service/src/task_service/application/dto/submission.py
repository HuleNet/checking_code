from dataclasses import dataclass
from uuid import UUID
from datetime import datetime


@dataclass(frozen=True)
class SubmissionDTO:
    id: UUID
    student_id: UUID
    group_assignment_id: UUID
    language: str
    code: str
    code_hash: str
    attempt_number: int
    status: str
    tests_total: int | None
    tests_passed: int | None
    checked_at: datetime | None
    created_at: datetime


@dataclass(frozen=True)
class CreateSubmissionDTO:
    student_id: UUID
    group_assignment_id: UUID
    language: str
    code: str
