from datetime import datetime, timezone

from task_service.application.use_cases.final_result import CreateFinalResultsUseCase
from task_service.application.ports import UnitOfWork
from task_service.application.errors import InternalError


class ScanExpiredGroupAssignmentsUseCase:
    def __init__(
        self,
        uow: UnitOfWork,
        create_final_results: CreateFinalResultsUseCase,
    ) -> None:
        self.uow = uow
        self.create_final_results = create_final_results

    async def execute(self, limit: int = 100) -> None:
        try:
            async with self.uow as uow:
                group_assignments = await uow.group_assignment_repo.claim_expired(
                    now=datetime.now(timezone.utc), limit=limit
                )

                if group_assignments:
                    for group_assignment in group_assignments:
                        await self.create_final_results.execute(
                            group_assignment_id=group_assignment.id
                        )

                    await uow.commit()

        except Exception as exc:
            raise InternalError(
                message="Failed to claim expired GroupAssignments",
                details={
                    "entity": "group_assignment",
                },
            ) from exc
