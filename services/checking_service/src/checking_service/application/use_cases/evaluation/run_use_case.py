from uuid import UUID

from checking_service.application.models.outbox import RunEvaluationRequested
from checking_service.application.ports import UnitOfWork
from checking_service.application.services import EvaluationService
from checking_service.application.errors import (
    ApplicationError,
    NotFoundError,
    ExecutionError,
    InternalError,
)


class RunEvaluationUseCase:
    def __init__(
        self,
        uow: UnitOfWork,
        evaluation_service: EvaluationService,
        stuck_time_sec: int,
    ) -> None:
        self.uow = uow
        self.evaluation_service = evaluation_service
        self.stuck_time_sec = stuck_time_sec

    async def execute(self, event: RunEvaluationRequested) -> None:
        try:
            async with self.uow as uow:
                evaluation_domain = await uow.evaluation_repo.claim_for_run(
                    id=event.evaluation_id,
                    stuck_timeout_sec=self.stuck_time_sec,
                )

                if evaluation_domain is None:
                    return

                execution_cases = await uow.execution_case_repo.get_by_evaluation(
                    evaluation_id=evaluation_domain.id
                )

                if not execution_cases:
                    raise NotFoundError(
                        message="ExecutionCases not found",
                        details={
                            "entity": "execution_case",
                            "evaluation_id": evaluation_domain.id,
                        },
                    )

                await uow.commit()

            try:
                execution_cases = await self.evaluation_service.execute(
                    code=event.code,
                    language=event.language,
                    execution_cases=execution_cases,
                )

            except ExecutionError:
                await self._mark_failed(evaluation_id=event.evaluation_id)
                raise

            async with self.uow as uow:
                evaluation_domain = await uow.evaluation_repo.get(
                    id=event.evaluation_id
                )

                if evaluation_domain is None:
                    raise NotFoundError(
                        message="Evaluation not found",
                        details={
                            "entity": "evaluation",
                            "id": event.evaluation_id,
                        },
                    )

                await uow.execution_case_repo.update_many(
                    execution_cases=execution_cases
                )
                evaluation_domain.recalculate(execution_cases=execution_cases)
                await uow.evaluation_repo.update(evaluation=evaluation_domain)
                await uow.commit()

        except ApplicationError:
            raise

        except Exception as exc:
            raise InternalError(
                message="Failed to run Evaluation",
                details={
                    "entity": "evaluation",
                    "evaluation_id": event.evaluation_id,
                    "assignment_id": event.assignment_id,
                },
            ) from exc

    async def _mark_failed(self, evaluation_id: UUID) -> None:
        try:
            async with self.uow as uow:
                evaluation_domain = await uow.evaluation_repo.get(id=evaluation_id)

                if evaluation_domain:
                    evaluation_domain.fail()
                    await uow.evaluation_repo.update(evaluation=evaluation_domain)
                    await uow.commit()

        except Exception:
            pass
