from uuid import UUID

from checking_service.application.dto.evaluation import EvaluationDTO
from checking_service.application.dto.mappers import EvaluationMapper
from checking_service.application.models.pagination import CursorPagination, Page
from checking_service.application.ports import UnitOfWork
from checking_service.application.errors import ApplicationError, InternalError


class GetEvaluationPageUseCase:
    def __init__(self, uow: UnitOfWork) -> None:
        self.uow = uow

    async def execute(
        self, submission_id: UUID, pagination: CursorPagination
    ) -> Page[EvaluationDTO]:
        try:
            async with self.uow as uow:
                domain_page = await uow.evaluation_repo.get_page(
                    submission_id=submission_id, pagination=pagination
                )

            return Page(
                items=[
                    EvaluationMapper.to_dto(domain=domain)
                    for domain in domain_page.items
                ],
                next_cursor=domain_page.next_cursor,
            )

        except ApplicationError:
            raise

        except Exception as exc:
            raise InternalError(
                message="Failed to get Evaluation page",
                details={
                    "entity": "evaluation",
                    "submission_id": submission_id,
                    "is_page": True,
                },
            ) from exc
