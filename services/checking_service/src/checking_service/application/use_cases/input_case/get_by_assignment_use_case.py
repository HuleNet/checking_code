from uuid import UUID

from checking_service.application.dto.input_case import InputCaseDTO
from checking_service.application.pagination import CursorPagination, Page
from checking_service.application.mappers import InputCaseMapper
from checking_service.application.ports import UnitOfWork


class GetInputCaseByAssignmentUseCase:
    def __init__(self, uow: UnitOfWork) -> None:
        self.uow = uow

    async def execute(
        self, assignment_id: UUID, pagination: CursorPagination
    ) -> Page[InputCaseDTO]:
        async with self.uow as uow:
            domain_page = await uow.input_case_repo.get_by_assignment(
                assignment_id=assignment_id, pagination=pagination
            )

        return Page(
            items=[
                InputCaseMapper.to_dto(domain=domain) for domain in domain_page.items
            ],
            next_cursor=domain_page.next_cursor,
        )
