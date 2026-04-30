from task_service.application.ports.repositories.assignment_repo import (
    AssignmentRepository,
)
from task_service.application.ports.repositories.group_assignment_repo import (
    GroupAssignmentRepository,
)
from task_service.application.ports.repositories.submission_repo import (
    SubmissionRepository,
)
from task_service.application.ports.repositories.final_result_repo import (
    FinalResultRepository,
)


__all__ = (
    "AssignmentRepository",
    "GroupAssignmentRepository",
    "SubmissionRepository",
    "FinalResultRepository",
)
