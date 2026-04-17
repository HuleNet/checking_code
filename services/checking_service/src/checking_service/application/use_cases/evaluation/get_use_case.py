from uuid import UUID

from checking_service.application.dto.evaluation import EvaluationDTO
from checking_service.application.mappers import EvaluationMapper
from checking_service.application.ports import UnitOfWork
from checking_service.application.errors import NotFoundError


class GetEvaluationUseCase:
    def __init__(self, uow: UnitOfWork) -> None:
        self.uow = uow

    async def execute(self, id: UUID) -> EvaluationDTO:
        async with self.uow as uow:
            domain_result = await uow.evaluation_repo.get(id=id)

        if domain_result is None:
            raise NotFoundError(
                message="Evaluation not found",
                details={
                    "id": id,
                },
            )

        return EvaluationMapper.to_dto(domain=domain_result)
