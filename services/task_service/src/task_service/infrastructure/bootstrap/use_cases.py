from collections.abc import Callable

from task_service.domain.services import ScoringService
from task_service.application.use_cases.assignment import (
    CreateAssignmentUseCase,
    GetAssignmentUseCase,
    GetAssignmentPageUseCase,
    UpdateAssignmentUseCase,
    DeleteAssignmentUseCase,
)
from task_service.application.use_cases.group_assignment import (
    CreateGroupAssignmentUseCase,
    GetGroupAssignmentUseCase,
    GetGroupAssignmentsByGroupUseCase,
    GetGroupAssignmentPageUseCase,
    DeleteGroupAssignmentUseCase,
)
from task_service.application.use_cases.submission import (
    CreateSubmissionUseCase,
    GetSubmissionUseCase,
    GetSubmissionsByGroupAssignmentUseCase,
    GetSubmissionPageUseCase,
    DeleteSubmissionUseCase,
    FailSubmissionUseCase,
)
from task_service.application.use_cases.final_result import (
    CreateFinalResultsUseCase,
    GetFinalResultUseCase,
    GetFinalResultsByGroupAssignmentUseCase,
    GetFinalResultPageUseCase,
    DeleteFinalResultUseCase,
)
from task_service.application.use_cases.workflows import (
    ApplySubmissionResultUseCase,
    ScanExpiredGroupAssignmentsUseCase,
)
from task_service.application.ports import UnitOfWork, CheckingService
from task_service.infrastructure.core.settings import Settings


class UseCases:
    def __init__(
        self,
        uow_factory: Callable[[], UnitOfWork],
        scoring_service: ScoringService,
        checking_service: CheckingService,
        settings: Settings,
    ) -> None:
        self.uow_factory = uow_factory
        self.scoring_service = scoring_service
        self.checking_service = checking_service
        self.settings = settings

    @property
    def create_assignment(self) -> CreateAssignmentUseCase:
        return CreateAssignmentUseCase(uow=self.uow_factory())

    @property
    def get_assignment(self) -> GetAssignmentUseCase:
        return GetAssignmentUseCase(uow=self.uow_factory())

    @property
    def get_assignment_page(self) -> GetAssignmentPageUseCase:
        return GetAssignmentPageUseCase(uow=self.uow_factory())

    @property
    def update_assignment(self) -> UpdateAssignmentUseCase:
        return UpdateAssignmentUseCase(uow=self.uow_factory())

    @property
    def delete_assignment(self) -> DeleteAssignmentUseCase:
        return DeleteAssignmentUseCase(uow=self.uow_factory())

    @property
    def create_group_assignment(self) -> CreateGroupAssignmentUseCase:
        return CreateGroupAssignmentUseCase(uow=self.uow_factory())

    @property
    def get_group_assignment(self) -> GetGroupAssignmentUseCase:
        return GetGroupAssignmentUseCase(uow=self.uow_factory())

    @property
    def get_group_assignments_by_group(self) -> GetGroupAssignmentsByGroupUseCase:
        return GetGroupAssignmentsByGroupUseCase(uow=self.uow_factory())

    @property
    def get_group_assignment_page(self) -> GetGroupAssignmentPageUseCase:
        return GetGroupAssignmentPageUseCase(uow=self.uow_factory())

    @property
    def delete_group_assignment(self) -> DeleteGroupAssignmentUseCase:
        return DeleteGroupAssignmentUseCase(uow=self.uow_factory())

    @property
    def create_submission(self) -> CreateSubmissionUseCase:
        return CreateSubmissionUseCase(
            uow=self.uow_factory(),
            max_attempts=self.settings.max_attempts,
            checking_service=self.checking_service,
        )

    @property
    def get_submission(self) -> GetSubmissionUseCase:
        return GetSubmissionUseCase(uow=self.uow_factory())

    @property
    def get_submissions_by_group_assignment(
        self,
    ) -> GetSubmissionsByGroupAssignmentUseCase:
        return GetSubmissionsByGroupAssignmentUseCase(uow=self.uow_factory())

    @property
    def get_submission_page(self) -> GetSubmissionPageUseCase:
        return GetSubmissionPageUseCase(uow=self.uow_factory())

    @property
    def delete_submission(self) -> DeleteSubmissionUseCase:
        return DeleteSubmissionUseCase(uow=self.uow_factory())

    @property
    def fail_submission(self) -> FailSubmissionUseCase:
        return FailSubmissionUseCase(uow=self.uow_factory())

    @property
    def create_final_results(self) -> CreateFinalResultsUseCase:
        return CreateFinalResultsUseCase(
            uow=self.uow_factory(), scoring_service=self.scoring_service
        )

    @property
    def get_final_result(self) -> GetFinalResultUseCase:
        return GetFinalResultUseCase(uow=self.uow_factory())

    @property
    def get_final_results_by_group_assignment(
        self,
    ) -> GetFinalResultsByGroupAssignmentUseCase:
        return GetFinalResultsByGroupAssignmentUseCase(uow=self.uow_factory())

    @property
    def get_final_result_page(self) -> GetFinalResultPageUseCase:
        return GetFinalResultPageUseCase(uow=self.uow_factory())

    @property
    def delete_final_result(self) -> DeleteFinalResultUseCase:
        return DeleteFinalResultUseCase(uow=self.uow_factory())

    @property
    def apply_submission_result(self) -> ApplySubmissionResultUseCase:
        return ApplySubmissionResultUseCase(
            uow=self.uow_factory(), fail_submission=self.fail_submission
        )

    @property
    def scan_expired_group_assignments(self) -> ScanExpiredGroupAssignmentsUseCase:
        return ScanExpiredGroupAssignmentsUseCase(
            uow=self.uow_factory(), create_final_results=self.create_final_results
        )
