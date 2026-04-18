from uuid import UUID

from checking_service.application.dto.evaluation import EvaluationDTO
from checking_service.application.dto.mappers import EvaluationMapper
from checking_service.application.ports import UnitOfWork


class GetEvaluationsBySubmissionUseCase:
    def __init__(self, uow: UnitOfWork) -> None:
        self.uow = uow

    async def execute(self, submission_id: UUID) -> list[EvaluationDTO]:
        async with self.uow as uow:
            domain_results = await uow.evaluation_repo.get_by_submission(
                submission_id=submission_id
            )

        return [EvaluationMapper.to_dto(domain=domain) for domain in domain_results]
