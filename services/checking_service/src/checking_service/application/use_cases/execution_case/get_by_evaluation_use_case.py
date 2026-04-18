from uuid import UUID

from checking_service.application.dto.execution_case import ExecutionCaseDTO
from checking_service.application.dto.mappers import ExecutionCaseMapper
from checking_service.application.ports import UnitOfWork


class GetExecutionCasesByEvaluationUseCase:
    def __init__(self, uow: UnitOfWork) -> None:
        self.uow = uow

    async def execute(self, evaluation_id: UUID) -> list[ExecutionCaseDTO]:
        async with self.uow as uow:
            domain_results = await uow.execution_case_repo.get_by_evaluation(
                evaluation_id=evaluation_id
            )

        return [ExecutionCaseMapper.to_dto(domain=domain) for domain in domain_results]
