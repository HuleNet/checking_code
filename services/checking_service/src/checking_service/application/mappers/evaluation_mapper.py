from checking_service.domain.enums import Language, EvaluationStatus
from checking_service.domain.entities import Evaluation
from checking_service.application.dto.evaluation import EvaluationDTO
from checking_service.application.errors import ValidationError


class EvaluationMapper:
    @staticmethod
    def to_domain(dto: EvaluationDTO) -> Evaluation:
        try:
            language = Language(dto.language)

        except ValueError:
            raise ValidationError(
                message="Unsupported language",
                details={
                    "language": dto.language,
                },
            )

        try:
            status = EvaluationStatus(dto.status)

        except ValueError:
            raise ValidationError(
                message="Unsupported evaluation status",
                details={
                    "evaluation_status": dto.status,
                },
            )

        return Evaluation(
            id=dto.id,
            submission_id=dto.submission_id,
            language=language,
            total_tests_count=dto.total_tests_count,
            status=status,
            passed_tests=dto.passed_tests,
            failed_tests=dto.failed_tests,
            error_tests=dto.error_tests,
            created_at=dto.created_at,
        )

    @staticmethod
    def to_dto(domain: Evaluation) -> EvaluationDTO:
        return EvaluationDTO(
            id=domain.id,
            submission_id=domain.submission_id,
            language=domain.language.value,
            total_tests_count=domain.total_tests_count,
            status=domain.status.value,
            passed_tests=domain.passed_tests,
            failed_tests=domain.failed_tests,
            error_tests=domain.error_tests,
            created_at=domain.created_at,
        )
