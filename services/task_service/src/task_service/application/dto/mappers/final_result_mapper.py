from uuid import UUID

from task_service.domain.entities import FinalResult
from task_service.application.dto.final_result import (
    FinalResultDTO,
    CreateFinalResultDTO,
)


class FinalResultMapper:
    @staticmethod
    def to_domain(dto: CreateFinalResultDTO, id: UUID) -> FinalResult:
        return FinalResult(
            id=id,
            group_assignment_id=dto.group_assignment_id,
            student_id=dto.student_id,
            submission_id=dto.submission_id,
            score=dto.score,
            attempt_number=dto.attempt_number,
            tests_total=dto.tests_total,
            tests_passed=dto.tests_passed,
            plagiarism_score=dto.plagiarism_score,
            plagiarism_flag=dto.plagiarism_flag,
        )

    @staticmethod
    def to_dto(domain: FinalResult) -> FinalResultDTO:
        return FinalResultDTO(
            id=domain.id,
            group_assignment_id=domain.group_assignment_id,
            student_id=domain.student_id,
            submission_id=domain.submission_id,
            score=domain.score,
            attempt_number=domain.attempt_number,
            tests_total=domain.tests_total,
            tests_passed=domain.tests_passed,
            plagiarism_score=domain.plagiarism_score,
            plagiarism_flag=domain.plagiarism_flag,
            finalized_at=domain.finalized_at,
        )
