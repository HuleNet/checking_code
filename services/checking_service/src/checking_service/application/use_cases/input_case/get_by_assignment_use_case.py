from uuid import UUID

from checking_service.application.dto.input_case import InputCaseDTO
from checking_service.application.dto.mappers import InputCaseMapper
from checking_service.application.ports import UnitOfWork


class GetInputCasesByAssignmentUseCase:
    def __init__(self, uow: UnitOfWork) -> None:
        self.uow = uow

    async def execute(self, assignment_id: UUID) -> list[InputCaseDTO]:
        async with self.uow as uow:
            domain_results = await uow.input_case_repo.get_by_assignment(
                assignment_id=assignment_id
            )

        return [InputCaseMapper.to_dto(domain=domain) for domain in domain_results]
