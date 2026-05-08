from uuid import UUID

from task_service.application.ports.checking_service import (
    CheckingService,
)
from task_service.application.ports.task_dispatcher import (
    TaskDispatcher,
)
from task_service.application.use_cases.submission import (
    FailSubmissionUseCase,
    GetSubmissionUseCase,
    SetSubmissionEvaluationUseCase,
    StartSubmissionProcessingUseCase,
)
from task_service.domain.value_objects import SubmissionStatus


class ProcessSubmissionUseCase:
    def __init__(
        self,
        checking_service: CheckingService,
        task_dispatcher: TaskDispatcher,
        get_submission: GetSubmissionUseCase,
        start_submission_processing: StartSubmissionProcessingUseCase,
        set_submission_evaluation: SetSubmissionEvaluationUseCase,
        fail_submission: FailSubmissionUseCase,
    ) -> None:
        self.checking_service = checking_service
        self.task_dispatcher = task_dispatcher
        self.get_submission = get_submission
        self.start_submission_processing = start_submission_processing
        self.set_submission_evaluation = set_submission_evaluation
        self.fail_submission = fail_submission

    async def execute(self, submission_id: UUID) -> None:
        submission = await self.get_submission.execute(
            id=submission_id,
        )

        if submission.status != SubmissionStatus.PENDING:
            return

        await self.start_submission_processing.execute(
            id=submission.id,
        )

        try:
            evaluation = await self.checking_service.start_evaluation(
                submission_id=submission.id,
                assignment_id=submission.assignment_id,
                language=submission.language,
                code=submission.code,
            )

            await self.set_submission_evaluation.execute(
                id=submission.id,
                evaluation_id=UUID(evaluation.id),
            )

        except Exception:
            await self.fail_submission.execute(
                id=submission.id,
            )
            raise

        await self.task_dispatcher.poll_submission_result(
            submission_id=submission.id,
            evaluation_id=UUID(evaluation.id),
        )
