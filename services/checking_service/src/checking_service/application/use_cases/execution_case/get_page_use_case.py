from uuid import UUID

from checking_service.application.dto.execution_case import ExecutionCaseDTO
from checking_service.application.dto.mappers import ExecutionCaseMapper
from checking_service.application.models.pagination import CursorPagination, Page
from checking_service.application.ports import UnitOfWork
from checking_service.application.errors import ApplicationError, InternalError


class GetExecutionCasePageUseCase:
    def __init__(self, uow: UnitOfWork) -> None:
        self.uow = uow

    async def execute(
        self, evaluation_id: UUID, pagination: CursorPagination
    ) -> Page[ExecutionCaseDTO]:
        try:
            async with self.uow as uow:
                domain_page = await uow.execution_case_repo.get_page(
                    evaluation_id=evaluation_id, pagination=pagination
                )

            return Page(
                items=[
                    ExecutionCaseMapper.to_dto(domain=domain)
                    for domain in domain_page.items
                ],
                next_cursor=domain_page.next_cursor,
            )

        except ApplicationError:
            raise

        except Exception as exc:
            raise InternalError(
                message="Failed to get ExecutionCase page",
                details={
                    "entity": "execution_case",
                    "evaluation_id": evaluation_id,
                    "is_page": True,
                },
            ) from exc
