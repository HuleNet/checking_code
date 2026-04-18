from uuid import UUID

from checking_service.application.dto.evaluation import EvaluationDTO
from checking_service.application.dto.mappers import EvaluationMapper
from checking_service.application.ports import UnitOfWork
from checking_service.application.errors import NotFoundError


class DeleteEvaluationUseCase:
    def __init__(self, uow: UnitOfWork) -> None:
        self.uow = uow

    async def execute(self, id: UUID) -> EvaluationDTO:
        async with self.uow as uow:
            domain_result = await uow.evaluation_repo.delete(id=id)

        if domain_result is None:
            raise NotFoundError(
                message="Evaluation not found",
                details={
                    "id": id,
                },
            )

        return EvaluationMapper.to_dto(domain=domain_result)
