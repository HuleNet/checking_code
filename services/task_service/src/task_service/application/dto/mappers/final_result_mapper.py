from task_service.domain.entities import FinalResult
from task_service.application.dto.final_result import (
    FinalResultDTO,
)


class FinalResultMapper:
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
            evaluation_status=domain.evaluation_status,
            finalized_at=domain.finalized_at,
        )
