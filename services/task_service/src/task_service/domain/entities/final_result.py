from dataclasses import dataclass, field
from uuid import UUID
from datetime import datetime, timezone


@dataclass
class FinalResult:
    id: UUID
    group_assignment_id: UUID
    student_id: UUID
    submission_id: UUID
    score: int
    tests_total: int
    tests_passed: int
    plagiarism_score: float | None = None
    plagiarism_flag: bool | None = None
    finalized_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
