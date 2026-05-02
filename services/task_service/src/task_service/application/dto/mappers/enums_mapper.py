from task_service.domain.enums import Language, SubmissionStatus
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

    @staticmethod
    def map_submission_status(submission_status: str) -> SubmissionStatus:
        try:
            return SubmissionStatus(submission_status)

        except ValueError:
            raise ValidationError(
                message="Unsupported submission status",
                details={
                    "submission_status": submission_status,
                    "allowed": SubmissionStatus.values(),
                },
            )
