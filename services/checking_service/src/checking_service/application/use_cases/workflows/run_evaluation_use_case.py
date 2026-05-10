from uuid import UUID

from checking_service.domain.services import JudgeService
from checking_service.domain.errors import DomainError

from checking_service.application.dto.mappers import (
    DomainEnumsMapper,
)
from checking_service.application.ports import (
    Runner,
    UnitOfWork,
)
from checking_service.application.errors import (
    ExecutionError,
    ValidationError,
    ApplicationError,
    InternalError,
)


class RunEvaluationUseCase:
    def __init__(
        self,
        uow: UnitOfWork,
        judge: JudgeService,
        runner: Runner,
        stuck_timeout_sec: int,
    ) -> None:
        self.uow = uow
        self.judge = judge
        self.runner = runner
        self.stuck_timeout_sec = stuck_timeout_sec

    async def execute(
        self,
        evaluation_id: UUID,
        code: str,
        language: str,
    ) -> None:
        try:
            async with self.uow as uow:
                evaluation = await uow.evaluation_repo.claim_for_run(
                    id=evaluation_id,
                    stuck_timeout_sec=self.stuck_timeout_sec,
                )

                if evaluation is None:
                    return

                execution_cases = await uow.execution_case_repo.get_by_evaluation(
                    evaluation_id=evaluation_id,
                )

                runner_results = await self.runner.run(
                    code=code,
                    language=DomainEnumsMapper.map_language(language),
                    execution_cases=execution_cases,
                )
                execution_case_map = {
                    execution_case.id: execution_case
                    for execution_case in execution_cases
                }
                seen_ids = set()
                for runner_result in runner_results:
                    if runner_result.id in seen_ids:
                        raise ExecutionError(
                            message="Duplicate ExecutionCase id",
                            details={
                                "execution_case_id": runner_result.id,
                                "reason": "duplicate_id",
                            },
                        )
                    seen_ids.add(runner_result.id)
                    execution_case = execution_case_map.get(runner_result.id)
                    if execution_case is None:
                        raise ExecutionError(
                            message="Unknown ExecutionCase id",
                            details={
                                "execution_case_id": runner_result.id,
                                "reason": "unknown_execution_case",
                            },
                        )
                    execution_case.apply_result(
                        stdout=runner_result.stdout,
                        stderr=runner_result.stderr,
                        execution_time_ms=(runner_result.execution_time_ms),
                        exit_code=runner_result.exit_code,
                        is_timeout=runner_result.is_timeout,
                        is_memory_exceeded=(runner_result.is_memory_exceeded),
                    )
                if len(seen_ids) != len(execution_cases):
                    missing_ids = set(execution_case_map) - seen_ids
                    raise ExecutionError(
                        message="Missing ExecutionCase results",
                        details={
                            "missing_execution_case_ids": [
                                str(id_) for id_ in missing_ids
                            ],
                            "expected_count": len(execution_cases),
                            "actual_count": len(seen_ids),
                        },
                    )

                judge_result = self.judge.evaluate(
                    execution_cases=execution_cases,
                )
                evaluation.apply_results(evaluation_result=judge_result)

                await uow.execution_case_repo.update_many(
                    execution_cases=execution_cases,
                )
                await uow.evaluation_repo.update(
                    evaluation=evaluation,
                )
                await uow.track(evaluation)
                await uow.commit()

        except DomainError as exc:
            raise ValidationError(
                message=exc.message,
                details=exc.details,
            ) from exc

        except ApplicationError:
            raise

        except Exception as exc:
            raise InternalError(
                message="Failed to run Evaluation",
                details={
                    "entity": "evaluation",
                    "evaluation_id": str(evaluation_id),
                },
            ) from exc
