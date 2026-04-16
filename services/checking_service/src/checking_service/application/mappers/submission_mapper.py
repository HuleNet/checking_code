from checking_service.domain.enums import Language
from checking_service.domain.entities import Submission
from checking_service.application.dto.submission import SubmissionDTO
from checking_service.application.errors import ValidationError


class SubmissionMapper:
    @staticmethod
    def to_domain(dto: SubmissionDTO) -> Submission:
        try:
            return Submission(
                id=dto.id,
                assignment_id=dto.assignment_id,
                language=Language(dto.language),
                code=dto.code,
            )

        except ValueError:
            raise ValidationError(
                message="Unsupported language",
                details={
                    "language": dto.language,
                },
            )
