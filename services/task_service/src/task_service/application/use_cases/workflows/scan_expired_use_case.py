from datetime import datetime, timezone

from task_service.application.ports import UnitOfWork, TaskDispatcher
from task_service.application.errors import InternalError


class ScanExpiredGroupAssignmentsUseCase:
    def __init__(
        self,
        uow: UnitOfWork,
        task_dispatcher: TaskDispatcher,
    ) -> None:
        self.uow = uow
        self.task_dispatcher = task_dispatcher

    async def execute(self, limit: int = 100) -> None:
        try:
            async with self.uow as uow:
                expired = await uow.group_assignment_repo.claim_expired(
                    now=datetime.now(timezone.utc), limit=limit
                )
                await uow.commit()

        except Exception as exc:
            raise InternalError(
                message="Failed to claim expired GroupAssignments",
                details={
                    "entity": "group_assignment",
                },
            ) from exc

        for group_assignment in expired:
            await self.task_dispatcher.finalize_group_assignment(
                group_assignment_id=group_assignment.id
            )
