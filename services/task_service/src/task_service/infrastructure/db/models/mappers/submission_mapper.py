from typing import Any

from task_service.domain.value_objects import CodeHash
from task_service.domain.entities import Submission
from task_service.infrastructure.db.models import SubmissionORM


class SubmissionMapper:
    @staticmethod
    def to_domain(orm: SubmissionORM) -> Submission:
        return Submission(
            id=orm.id,
            student_id=orm.student_id,
            assignment_id=orm.assignment_id,
            group_assignment_id=orm.group_assignment_id,
            language=orm.language,
            code=orm.code,
            code_hash=CodeHash(orm.code_hash),
            attempt_number=orm.attempt_number,
            status=orm.status,
            tests_passed=orm.tests_passed,
            tests_total=orm.tests_total,
            evaluation_id=orm.evaluation_id,
            checked_at=orm.checked_at,
            created_at=orm.created_at,
        )

    @staticmethod
    def to_dict(domain: Submission) -> dict[str, Any]:
        return {
            "id": domain.id,
            "student_id": domain.student_id,
            "assignment_id": domain.assignment_id,
            "group_assignment_id": domain.group_assignment_id,
            "language": domain.language,
            "code": domain.code,
            "code_hash": domain.code_hash.value,
            "attempt_number": domain.attempt_number,
            "status": domain.status,
            "tests_passed": domain.tests_passed,
            "tests_total": domain.tests_total,
            "evaluation_id": domain.evaluation_id,
            "checked_at": domain.checked_at,
            "created_at": domain.created_at,
        }
