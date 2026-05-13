from task_service.infrastructure.db.repositories.assignment_repo import (
    SQLAlchemyAssignmentRepository,
)
from task_service.infrastructure.db.repositories.group_assignment_repo import (
    SQLAlchemyGroupAssignmentRepository,
)
from task_service.infrastructure.db.repositories.submission_repo import (
    SQLAlchemySubmissionRepository,
)
from task_service.infrastructure.db.repositories.final_result_repo import (
    SQLAlchemyFinalResultRepository,
)


__all__ = (
    "SQLAlchemyAssignmentRepository",
    "SQLAlchemyGroupAssignmentRepository",
    "SQLAlchemySubmissionRepository",
    "SQLAlchemyFinalResultRepository",
)
