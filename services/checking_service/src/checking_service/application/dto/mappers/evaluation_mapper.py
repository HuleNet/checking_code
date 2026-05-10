from uuid import UUID

from checking_service.domain.entities import Evaluation
from checking_service.application.dto.evaluation import (
    EvaluationDTO,
    CreateEvaluationDTO,
)


class EvaluationMapper:
    @staticmethod
    def to_domain(dto: CreateEvaluationDTO, id: UUID) -> Evaluation:
        return Evaluation.create(
            id=id,
            submission_id=dto.submission_id,
            tests_total=dto.tests_total,
        )

    @staticmethod
    def to_dto(domain: Evaluation) -> EvaluationDTO:
        return EvaluationDTO(
            id=domain.id,
            submission_id=domain.submission_id,
            tests_total=domain.tests_total,
            tests_passed=domain.tests_passed,
            status=domain.status.value,
            created_at=domain.created_at,
            started_at=domain.started_at,
        )
