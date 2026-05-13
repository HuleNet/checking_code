from checking_service.domain.value_objects import (
    Language,
    CheckType,
    EvaluationStatus,
)
from checking_service.application.errors import ValidationError


class DomainEnumsMapper:
    @staticmethod
    def map_language(language: str) -> Language:
        try:
            return Language(language)

        except ValueError:
            raise ValidationError(
                message="Unsupported language",
                details={
                    "language": language,
                    "allowed": Language.values(),
                },
            )

    @staticmethod
    def map_check_type(check_type: str) -> CheckType:
        try:
            return CheckType(check_type)

        except ValueError:
            raise ValidationError(
                message="Unsupported check type",
                details={
                    "check_type": check_type,
                    "allowed": CheckType.values(),
                },
            )

    @staticmethod
    def map_evaluation_status(evaluation_status: str) -> EvaluationStatus:
        try:
            return EvaluationStatus(evaluation_status)

        except ValueError:
            raise ValidationError(
                message="Unsupported evaluation status",
                details={
                    "evaluation_status": evaluation_status,
                    "allowed": EvaluationStatus.values(),
                },
            )
