from typing import Any

from checking_service.domain.entities import Evaluation
from checking_service.infrastructure.db.models import EvaluationORM


class EvaluationMapper:
    @staticmethod
    def to_domain(orm: EvaluationORM) -> Evaluation:
        return Evaluation(
            id=orm.id,
            submission_id=orm.submission_id,
            total_tests_count=orm.total_tests_count,
            passed_tests_count=orm.passed_tests_count,
            status=orm.status,
            created_at=orm.created_at,
            started_at=orm.started_at,
        )

    @staticmethod
    def to_dict(domain: Evaluation) -> dict[str, Any]:
        return {
            "id": domain.id,
            "submission_id": domain.submission_id,
            "total_tests_count": domain.total_tests_count,
            "passed_tests_count": domain.passed_tests_count,
            "status": domain.status,
            "created_at": domain.created_at,
            "started_at": domain.started_at,
        }
