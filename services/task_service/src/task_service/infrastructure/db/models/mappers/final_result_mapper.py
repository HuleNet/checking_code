from typing import Any, cast

from task_service.domain.value_objects import EvaluationStatus
from task_service.domain.entities import FinalResult
from task_service.infrastructure.db.models import FinalResultORM


class FinalResultMapper:
    @staticmethod
    def to_domain(orm: FinalResultORM) -> FinalResult:
        return FinalResult(
            id=orm.id,
            group_assignment_id=orm.group_assignment_id,
            student_id=orm.student_id,
            submission_id=orm.submission_id,
            score=orm.score,
            attempt_number=orm.attempt_number,
            tests_total=orm.tests_total,
            tests_passed=orm.tests_passed,
            evaluation_status=cast(EvaluationStatus, orm.evaluation_status),
            finalized_at=orm.finalized_at,
        )

    @staticmethod
    def to_dict(domain: FinalResult) -> dict[str, Any]:
        return {
            "id": domain.id,
            "group_assignment_id": domain.group_assignment_id,
            "student_id": domain.student_id,
            "submission_id": domain.submission_id,
            "score": domain.score,
            "attempt_number": domain.attempt_number,
            "tests_total": domain.tests_total,
            "tests_passed": domain.tests_passed,
            "evaluation_status": domain.evaluation_status,
            "finalized_at": domain.finalized_at,
        }
