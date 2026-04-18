from checking_service.application.models.outbox import RunEvaluationRequested
from checking_service.application.ports import UnitOfWork
from checking_service.application.services import ExecutionService
from checking_service.application.errors import NotFoundError


class RunEvaluationUseCase:
    def __init__(
        self, uow: UnitOfWork, execution_service: ExecutionService, stuck_time_sec: int
    ) -> None:
        self.uow = uow
        self.execution_service = execution_service
        self.stuck_time_sec = stuck_time_sec

    async def execute(self, event: RunEvaluationRequested) -> None:
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
                        "evaluation_id": evaluation_domain.id,
                    },
                )

            await uow.commit()

        try:
            execution_cases = await self.execution_service.execute(
                code=event.code,
                language=event.language,
                execution_cases=execution_cases,
            )

        # !ЗАМЕНИТЬ НА INFRA-ERROR!
        except Exception:
            async with self.uow as uow:
                evaluation_domain = await uow.evaluation_repo.get(
                    id=event.evaluation_id
                )

                if evaluation_domain:
                    evaluation_domain.fail()
                    await uow.evaluation_repo.update(evaluation=evaluation_domain)
                    await uow.commit()

            raise

        async with self.uow as uow:
            evaluation_domain = await uow.evaluation_repo.get(id=event.evaluation_id)

            if evaluation_domain is None:
                raise NotFoundError(
                    message="Evaluation not found",
                    details={
                        "id": event.evaluation_id,
                    },
                )

            await uow.execution_case_repo.update_many(execution_cases=execution_cases)
            evaluation_domain.recalculate(execution_cases=execution_cases)
            await uow.evaluation_repo.update(evaluation=evaluation_domain)
            await uow.commit()
