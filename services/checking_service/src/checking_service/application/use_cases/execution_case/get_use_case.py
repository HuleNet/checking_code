from uuid import UUID

from checking_service.application.dto.execution_case import ExecutionCaseDTO
from checking_service.application.dto.mappers import ExecutionCaseMapper
from checking_service.application.ports import UnitOfWork
from checking_service.application.errors import NotFoundError


class GetExecutionCaseUseCase:
    def __init__(self, uow: UnitOfWork) -> None:
        self.uow = uow

    async def execute(self, id: UUID) -> ExecutionCaseDTO:
        async with self.uow as uow:
            domain_result = await uow.execution_case_repo.get(id=id)

        if domain_result is None:
            raise NotFoundError(
                message="ExecutionCase not found",
                details={
                    "id": id,
                },
            )

        return ExecutionCaseMapper.to_dto(domain=domain_result)
