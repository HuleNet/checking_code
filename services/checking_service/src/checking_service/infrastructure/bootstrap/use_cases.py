from collections.abc import Callable

from checking_service.domain.services import JudgeService
from checking_service.application.use_cases.test_case import (
    CreateTestCaseUseCase,
    GetTestCaseUseCase,
    GetTestCasesByAssignmentUseCase,
    GetTestCasePageUseCase,
    UpdateTestCaseUseCase,
    DeleteTestCaseUseCase,
)
from checking_service.application.use_cases.evaluation import (
    GetEvaluationUseCase,
    GetEvaluationsBySubmissionUseCase,
    GetEvaluationPageUseCase,
    DeleteEvaluationUseCase,
)
from checking_service.application.use_cases.execution_case import (
    GetExecutionCaseUseCase,
    GetExecutionCasesByEvaluationUseCase,
    GetExecutionCasePageUseCase,
)
from checking_service.application.use_cases.workflows import (
    CreateEvaluationUseCase,
    RunEvaluationUseCase,
    PreviewRunEvaluationUseCase,
    PublishOutboxEventsUseCase,
)
from checking_service.application.ports import UnitOfWork, TaskDispatcher, Runner
from checking_service.infrastructure.core.settings import Settings


class UseCases:
    def __init__(
        self,
        uow_factory: Callable[[], UnitOfWork],
        judge_service: JudgeService,
        runner: Runner,
        task_dispatcher: TaskDispatcher,
        settings: Settings,
    ) -> None:
        self.uow_factory = uow_factory
        self.judge_service = judge_service
        self.runner = runner
        self.task_dispatcher = task_dispatcher
        self.settings = settings

    @property
    def create_test_case(self) -> CreateTestCaseUseCase:
        return CreateTestCaseUseCase(uow=self.uow_factory())

    @property
    def get_test_case(self) -> GetTestCaseUseCase:
        return GetTestCaseUseCase(uow=self.uow_factory())

    @property
    def get_test_cases_by_assignment(self) -> GetTestCasesByAssignmentUseCase:
        return GetTestCasesByAssignmentUseCase(uow=self.uow_factory())

    @property
    def get_test_case_page(self) -> GetTestCasePageUseCase:
        return GetTestCasePageUseCase(uow=self.uow_factory())

    @property
    def update_test_case(self) -> UpdateTestCaseUseCase:
        return UpdateTestCaseUseCase(uow=self.uow_factory())

    @property
    def delete_test_case(self) -> DeleteTestCaseUseCase:
        return DeleteTestCaseUseCase(uow=self.uow_factory())

    @property
    def get_evaluation(self) -> GetEvaluationUseCase:
        return GetEvaluationUseCase(uow=self.uow_factory())

    @property
    def get_evaluations_by_submission(self) -> GetEvaluationsBySubmissionUseCase:
        return GetEvaluationsBySubmissionUseCase(uow=self.uow_factory())

    @property
    def get_evaluation_page(self) -> GetEvaluationPageUseCase:
        return GetEvaluationPageUseCase(uow=self.uow_factory())

    @property
    def delete_evaluation(self) -> DeleteEvaluationUseCase:
        return DeleteEvaluationUseCase(uow=self.uow_factory())

    @property
    def get_execution_case(self) -> GetExecutionCaseUseCase:
        return GetExecutionCaseUseCase(uow=self.uow_factory())

    @property
    def get_execution_cases_by_evaluation(self) -> GetExecutionCasesByEvaluationUseCase:
        return GetExecutionCasesByEvaluationUseCase(uow=self.uow_factory())

    @property
    def get_execution_case_page(self) -> GetExecutionCasePageUseCase:
        return GetExecutionCasePageUseCase(uow=self.uow_factory())

    @property
    def create_evaluation(self) -> CreateEvaluationUseCase:
        return CreateEvaluationUseCase(
            uow=self.uow_factory(), get_test_cases=self.get_test_cases_by_assignment
        )

    @property
    def run_evaluation(self) -> RunEvaluationUseCase:
        return RunEvaluationUseCase(
            uow=self.uow_factory(),
            judge=self.judge_service,
            runner=self.runner,
            stuck_timeout_sec=self.settings.stuck_time_sec,
        )

    @property
    def preview_run_evaluation(self) -> PreviewRunEvaluationUseCase:
        return PreviewRunEvaluationUseCase(
            judge=self.judge_service,
            runner=self.runner,
            get_test_cases=self.get_test_cases_by_assignment,
        )

    @property
    def publish_outbox_events(self) -> PublishOutboxEventsUseCase:
        return PublishOutboxEventsUseCase(
            uow=self.uow_factory(), task_dispatcher=self.task_dispatcher
        )
