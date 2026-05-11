from typing import Any

from checking_service.domain.entities import Evaluation
from checking_service.infrastructure.db.models import EvaluationORM


class EvaluationMapper:
    @staticmethod
    def to_domain(orm: EvaluationORM) -> Evaluation:
        return Evaluation(
            id=orm.id,
            submission_id=orm.submission_id,
            tests_total=orm.tests_total,
            tests_passed=orm.tests_passed,
            status=orm.status,
            created_at=orm.created_at,
        )

    @staticmethod
    def to_dict(domain: Evaluation) -> dict[str, Any]:
        return {
            "id": domain.id,
            "submission_id": domain.submission_id,
            "tests_total": domain.tests_total,
            "tests_passed": domain.tests_passed,
            "status": domain.status,
            "created_at": domain.created_at,
        }
