from uuid import UUID

from task_service.domain.value_objects import CodeHash
from task_service.domain.entities import Submission
from task_service.application.dto.submission import SubmissionDTO, CreateSubmissionDTO
from task_service.application.dto.mappers import DomainEnumsMapper


class SubmissionMapper:
    @staticmethod
    def to_domain(
        dto: CreateSubmissionDTO, id: UUID, code_hash: CodeHash, attempt_number: int
    ) -> Submission:
        language = DomainEnumsMapper.map_language(language=dto.language)
        return Submission.create(
            id=id,
            student_id=dto.student_id,
            assignment_id=dto.assignment_id,
            group_assignment_id=dto.group_assignment_id,
            language=language,
            code=dto.code,
            code_hash=code_hash,
            attempt_number=attempt_number,
        )

    @staticmethod
    def to_dto(domain: Submission) -> SubmissionDTO:
        return SubmissionDTO(
            id=domain.id,
            student_id=domain.student_id,
            assignment_id=domain.assignment_id,
            group_assignment_id=domain.group_assignment_id,
            language=domain.language.value,
            code=domain.code,
            code_hash=domain.code_hash.value,
            attempt_number=domain.attempt_number,
            status=domain.status.value,
            tests_total=domain.tests_total,
            tests_passed=domain.tests_passed,
            evaluation_id=domain.evaluation_id,
            checked_at=domain.checked_at,
            created_at=domain.created_at,
        )
