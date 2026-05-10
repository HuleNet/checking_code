from checking_service.domain.value_objects import (
    Language,
    CheckType,
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
