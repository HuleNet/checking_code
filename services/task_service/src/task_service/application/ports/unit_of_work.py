from typing import Protocol

from task_service.application.ports.repositories import (
    AssignmentRepository,
    GroupAssignmentRepository,
    SubmissionRepository,
    FinalResultRepository,
)


class UnitOfWork(Protocol):
    assignment_repo: AssignmentRepository
    group_assignment_repo: GroupAssignmentRepository
    submission_repo: SubmissionRepository
    final_result_repo: FinalResultRepository

    async def __aenter__(self) -> "UnitOfWork": ...

    async def __aexit__(self, exc_type, exc, tb): ...

    async def commit(self) -> None: ...

    async def rollback(self) -> None: ...
