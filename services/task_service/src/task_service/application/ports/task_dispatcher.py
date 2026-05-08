from typing import Protocol
from uuid import UUID


class TaskDispatcher(Protocol):
    async def process_submission(
        self,
        submission_id: UUID,
    ) -> None: ...

    async def poll_submission_result(
        self, submission_id: UUID, evaluation_id: UUID, countdown: int = 5
    ) -> None: ...

    async def finalize_group_assignment(
        self,
        group_assignment_id: UUID,
    ) -> None: ...
