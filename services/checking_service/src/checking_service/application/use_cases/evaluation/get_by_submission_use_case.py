from uuid import UUID

from checking_service.application.dto.evaluation import EvaluationDTO
from checking_service.application.pagination import CursorPagination, Page
from checking_service.application.mappers import EvaluationMapper
from checking_service.application.ports import UnitOfWork


class GetEvaluationBySubmissionUseCase:
    def __init__(self, uow: UnitOfWork) -> None:
        self.uow = uow

    async def execute(
        self, submission_id: UUID, pagination: CursorPagination
    ) -> Page[EvaluationDTO]:
        async with self.uow as uow:
            domain_page = await uow.evaluation_repo.get_by_submission(
                submission_id=submission_id, pagination=pagination
            )

        return Page(
            items=[
                EvaluationMapper.to_dto(domain=domain) for domain in domain_page.items
            ],
            next_cursor=domain_page.next_cursor,
        )
