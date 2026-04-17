from uuid import UUID

from checking_service.domain.entities import Evaluation
from checking_service.application.dto.evaluation import (
    EvaluationDTO,
    CreateEvaluationDTO,
)


class EvaluationMapper:
    @staticmethod
    def to_domain(dto: CreateEvaluationDTO, id: UUID) -> Evaluation:
        return Evaluation(
            id=id,
            submission_id=dto.submission_id,
            total_tests_count=dto.total_tests_count,
        )

    @staticmethod
    def to_dto(domain: Evaluation) -> EvaluationDTO:
        return EvaluationDTO(
            id=domain.id,
            submission_id=domain.submission_id,
            total_tests_count=domain.total_tests_count,
            status=domain.status.value,
            passed_tests=domain.passed_tests,
            failed_tests=domain.failed_tests,
            error_tests=domain.error_tests,
            created_at=domain.created_at,
        )
