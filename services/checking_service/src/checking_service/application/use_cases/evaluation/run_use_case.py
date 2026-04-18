from checking_service.application.dto.outbox import RunEvaluationRequested
from checking_service.application.mappers import JudgeRequestMapper
from checking_service.application.ports import UnitOfWork, Runner, Judge
from checking_service.application.errors import NotFoundError


class RunEvaluationUseCase:
    def __init__(
        self, uow: UnitOfWork, runner: Runner, judge: Judge, stuck_time_sec: int
    ) -> None:
        self.uow = uow
        self.runner = runner
        self.judge = judge
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
            runner_results = await self.runner.run(
                code=event.code,
                language=event.language,
                execution_cases=execution_cases,
            )

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

            execution_case_map = {
                execution_case.id: execution_case for execution_case in execution_cases
            }

            for runner_result in runner_results:
                execution_case = execution_case_map.get(runner_result.execution_case_id)

                if execution_case is None:
                    raise NotFoundError(
                        message="ExecutionCase in runner results not found",
                        details={
                            "execution_case_id": runner_result.execution_case_id,
                        },
                    )
                request = JudgeRequestMapper.map_request(
                    execution_case=execution_case, runner_result=runner_result
                )
                status = self.judge.evaluate(request=request)
                execution_case.apply_result(
                    status=status,
                    stdout=runner_result.stdout,
                    stderr=runner_result.stderr,
                    execution_time_ms=runner_result.execution_time_ms,
                )

            await uow.execution_case_repo.update_many(execution_cases=execution_cases)
            evaluation_domain.recalculate(execution_cases=execution_cases)
            await uow.evaluation_repo.update(evaluation=evaluation_domain)
            await uow.commit()
