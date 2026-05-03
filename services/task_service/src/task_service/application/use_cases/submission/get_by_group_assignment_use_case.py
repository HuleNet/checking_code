from uuid import UUID

from task_service.application.dto.submission import SubmissionDTO
from task_service.application.dto.mappers import SubmissionMapper
from task_service.application.ports import UnitOfWork
from task_service.application.errors import ApplicationError, InternalError


class GetSubmissionsByGroupAssignmentUseCase:
    def __init__(self, uow: UnitOfWork) -> None:
        self.uow = uow

    async def execute(self, group_assignment_id: UUID) -> list[SubmissionDTO]:
        try:
            async with self.uow as uow:
                domain_results = await uow.submission_repo.get_by_group_assignment(
                    group_assignment_id=group_assignment_id
                )

            return [SubmissionMapper.to_dto(domain=domain) for domain in domain_results]

        except ApplicationError:
            raise

        except Exception as exc:
            raise InternalError(
                message="Failed to get Submissions",
                details={
                    "entity": "submission",
                    "group_assignment_id": group_assignment_id,
                    "is_page": False,
                },
            ) from exc
