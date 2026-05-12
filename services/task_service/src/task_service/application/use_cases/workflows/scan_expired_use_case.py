from datetime import datetime, timezone

from task_service.application.ports import UnitOfWork
from task_service.application.errors import InternalError


class ScanExpiredGroupAssignmentsUseCase:
    def __init__(self, uow: UnitOfWork) -> None:
        self.uow = uow

    async def execute(self, limit: int = 100) -> None:
        try:
            async with self.uow as uow:
                await uow.group_assignment_repo.claim_expired(
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
