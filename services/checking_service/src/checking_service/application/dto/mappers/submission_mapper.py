from uuid import uuid4

from checking_service.domain.entities import Submission
from checking_service.application.dto.submission import (
    SubmissionDTO,
    PreviewSubmissionDTO,
)
from checking_service.application.dto.mappers import DomainEnumsMapper


class SubmissionMapper:
    @staticmethod
    def to_domain(dto: SubmissionDTO) -> Submission:
        language = DomainEnumsMapper.map_language(language=dto.language)
        return Submission(
            id=dto.id,
            assignment_id=dto.assignment_id,
            language=language,
            code=dto.code,
        )

    @staticmethod
    def to_domain_from_preview(dto: PreviewSubmissionDTO) -> Submission:
        language = DomainEnumsMapper.map_language(language=dto.language)
        return Submission(
            id=uuid4(),
            assignment_id=dto.assignment_id,
            language=language,
            code=dto.code,
        )
