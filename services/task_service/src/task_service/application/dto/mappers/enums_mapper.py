from task_service.domain.value_objects import Language
from task_service.application.errors import ValidationError


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
