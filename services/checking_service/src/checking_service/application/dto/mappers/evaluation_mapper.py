from checking_service.domain.value_objects import EvaluationStatus
from checking_service.domain.entities import Evaluation
from checking_service.application.dto.evaluation import EvaluationDTO
from checking_service.application.dto.mappers import DomainEnumsMapper


class EvaluationMapper:
    @staticmethod
    def to_domain(dto: EvaluationDTO) -> Evaluation:
        return Evaluation(
            id=dto.id,
            submission_id=dto.submission_id,
            tests_total=dto.tests_total,
            tests_passed=dto.tests_passed,
            status=DomainEnumsMapper.map_evaluation_status(dto.status),
            created_at=dto.created_at,
        )

    @staticmethod
    def to_dto(domain: Evaluation) -> EvaluationDTO:
        return EvaluationDTO(
            id=domain.id,
            submission_id=domain.submission_id,
            tests_total=domain.tests_total,
            tests_passed=domain.tests_passed,
            status=domain.status.value
            if domain.status is not None
            else EvaluationStatus.ERROR,
            created_at=domain.created_at,
        )
