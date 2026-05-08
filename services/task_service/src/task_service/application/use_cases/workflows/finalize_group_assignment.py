from uuid import UUID

from task_service.application.use_cases.final_result import CreateFinalResultsUseCase
from task_service.application.ports import UnitOfWork
from task_service.application.errors import InternalError


class FinalizeGroupAssignmentUseCase:
    def __init__(
        self, uow: UnitOfWork, create_final_results: CreateFinalResultsUseCase
    ) -> None:
        self.uow = uow
        self.create_final_results = create_final_results

    async def execute(self, group_assignment_id: UUID) -> None:
        await self.create_final_results.execute(group_assignment_id=group_assignment_id)

        try:
            async with self.uow as uow:
                await uow.group_assignment_repo.finalize(id=group_assignment_id)
                await uow.commit()

        except Exception as exc:
            raise InternalError(
                message="Failed to finalize GroupAssignment",
                details={
                    "entity": "group_assignment",
                    "id": group_assignment_id,
                },
            ) from exc
