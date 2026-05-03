from dataclasses import dataclass
from uuid import UUID
from datetime import datetime


@dataclass(frozen=True)
class FinalResultDTO:
    id: UUID
    group_assignment_id: UUID
    student_id: UUID
    submission_id: UUID
    score: int
    attempt_number: int
    tests_total: int
    tests_passed: int
    plagiarism_score: float
    plagiarism_flag: bool
    finalized_at: datetime


@dataclass(frozen=True)
class CreateFinalResultDTO:
    group_assignment_id: UUID
    student_id: UUID
    submission_id: UUID
    score: int
    attempt_number: int
    tests_total: int
    tests_passed: int
    plagiarism_score: float
    plagiarism_flag: bool
