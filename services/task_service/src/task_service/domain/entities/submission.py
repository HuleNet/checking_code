from dataclasses import dataclass, field
from hashlib import sha256
from uuid import UUID
from datetime import datetime, timezone

from task_service.domain.enums import SubmissionStatus, TestStatus


@dataclass
class Submission:
    id: UUID
    student_id: UUID
    assignment_id: UUID
    group_assignment_id: UUID
    language: str
    code: str
    code_hash: str
    attempt_number: int
    tests_status: TestStatus | None
    tests_total: int | None
    tests_passed: int | None
    status: SubmissionStatus = SubmissionStatus.CREATED
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    checked_at: datetime | None = None
