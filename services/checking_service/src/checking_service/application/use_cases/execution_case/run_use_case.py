from checking_service.domain.entities import ExecutionCase
from checking_service.domain.errors import DomainError

from checking_service.application.dto.mappers import (
    DomainEnumsMapper,
)
from checking_service.application.ports import Runner
from checking_service.application.errors import (
    ExecutionError,
    ValidationError,
    ApplicationError,
    InternalError,
)


class RunExecutionCasesUseCase:
    def __init__(self, runner: Runner) -> None:
        self.runner = runner

    async def execute(
        self, code: str, language: str, execution_cases: list[ExecutionCase]
    ) -> list[ExecutionCase]:
        try:
            runner_results = await self.runner.run(
                code=code,
                language=DomainEnumsMapper.map_language(language),
                execution_cases=execution_cases,
            )
            execution_case_map = {
                execution_case.id: execution_case for execution_case in execution_cases
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

            return execution_cases

        except DomainError as exc:
            raise ValidationError(
                message=exc.message,
                details=exc.details,
            ) from exc

        except ApplicationError:
            raise

        except Exception as exc:
            raise InternalError(
                message="Failed to run ExecutionCases",
                details={
                    "entity": "execution_case",
                },
            ) from exc
