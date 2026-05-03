from uuid import UUID

from task_service.application.dto.final_result import FinalResultDTO
from task_service.application.dto.mappers import FinalResultMapper
from task_service.application.ports import UnitOfWork
from task_service.application.errors import ApplicationError, InternalError


class GetFinalResultsByGroupAssignmentUseCase:
    def __init__(self, uow: UnitOfWork) -> None:
        self.uow = uow

    async def execute(self, group_assignment_id: UUID) -> list[FinalResultDTO]:
        try:
            async with self.uow as uow:
                domain_results = await uow.final_result_repo.get_by_group_assignment(
                    group_assignment_id=group_assignment_id
                )

            return [
                FinalResultMapper.to_dto(domain=domain) for domain in domain_results
            ]

        except ApplicationError:
            raise

        except Exception as exc:
            raise InternalError(
                message="Failed to get FinalResults",
                details={
                    "entity": "final_result",
                    "group_assignment_id": group_assignment_id,
                    "is_page": False,
                },
            ) from exc
