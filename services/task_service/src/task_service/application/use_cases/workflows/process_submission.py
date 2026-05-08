from uuid import UUID

from task_service.domain.value_objects import SubmissionStatus
from task_service.application.dto.submission import ApplySubmissionResultDTO
from task_service.application.use_cases.submission import (
    GetSubmissionUseCase,
    StartSubmissionProcessingUseCase,
    ApplySubmissionResultUseCase,
    FailSubmissionUseCase,
)
from task_service.application.ports.checking_service import CheckingService


class ProcessSubmissionUseCase:
    def __init__(
        self,
        checking_service: CheckingService,
        get_submission: GetSubmissionUseCase,
        start_submission_processing: StartSubmissionProcessingUseCase,
        apply_submission_result: ApplySubmissionResultUseCase,
        fail_submission: FailSubmissionUseCase,
    ) -> None:
        self.checking_service = checking_service
        self.get_submission = get_submission
        self.start_submission_processing = start_submission_processing
        self.apply_submission_result = apply_submission_result
        self.fail_submission = fail_submission

    async def execute(self, submission_id: UUID) -> None:
        submission = await self.get_submission.execute(id=submission_id)

        if submission.status != SubmissionStatus.PENDING:
            return

        await self.start_submission_processing.execute(id=submission.id)

        try:
            result = await self.checking_service.evaluate_submission(
                submission_id=submission.id,
                assignment_id=submission.assignment_id,
                language=submission.language,
                code=submission.code,
            )

        except Exception:
            await self.fail_submission.execute(id=submission.id)
            raise

        await self.apply_submission_result.execute(
            dto=ApplySubmissionResultDTO(
                id=submission.id,
                tests_passed=result.tests_passed,
                tests_total=result.tests_total,
            )
        )
