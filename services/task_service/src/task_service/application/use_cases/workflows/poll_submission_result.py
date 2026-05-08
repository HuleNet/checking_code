from uuid import UUID

from task_service.domain.value_objects import SubmissionStatus
from task_service.application.dto.submission import ApplySubmissionResultDTO
from task_service.application.ports import CheckingService, TaskDispatcher
from task_service.application.use_cases.submission import (
    ApplySubmissionResultUseCase,
    FailSubmissionUseCase,
    GetSubmissionUseCase,
)


class PollSubmissionResultUseCase:
    def __init__(
        self,
        checking_service: CheckingService,
        task_dispatcher: TaskDispatcher,
        get_submission: GetSubmissionUseCase,
        apply_submission_result: ApplySubmissionResultUseCase,
        fail_submission: FailSubmissionUseCase,
    ) -> None:
        self.checking_service = checking_service
        self.task_dispatcher = task_dispatcher
        self.get_submission = get_submission
        self.apply_submission_result = apply_submission_result
        self.fail_submission = fail_submission

    async def execute(self, submission_id: UUID, evaluation_id: UUID) -> None:
        submission = await self.get_submission.execute(
            id=submission_id,
        )

        if submission.status != SubmissionStatus.IN_PROGRESS:
            return

        evaluation = await self.checking_service.get_evaluation(
            evaluation_id=str(evaluation_id),
        )

        if evaluation.status in ("PENDING", "RUNNING"):
            await self.task_dispatcher.poll_submission_result(
                submission_id=submission_id,
                evaluation_id=evaluation_id,
                countdown=5,
            )
            return

        if evaluation.status == "ERROR":
            await self.fail_submission.execute(
                id=submission_id,
            )
            return

        await self.apply_submission_result.execute(
            dto=ApplySubmissionResultDTO(
                id=submission_id,
                tests_passed=evaluation.tests_passed or 0,
                tests_total=evaluation.tests_total or 0,
            )
        )
