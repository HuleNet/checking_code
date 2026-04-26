from logging import getLogger

from checking_service.domain.enums import ExecutionStatus, Language
from checking_service.domain.entities import ExecutionCase
from checking_service.application.models.enums import PreviewEvaluationStatus
from checking_service.application.models.factories import JudgeRequestFactory
from checking_service.application.ports import Runner
from checking_service.application.services import JudgeService
from checking_service.application.errors import ExecutionError, ExecutionContractError


logger = getLogger(__name__)


class EvaluationService:
    def __init__(
        self,
        runner: Runner,
        judge: JudgeService,
        max_stdio_length: int,
    ) -> None:
        self.runner = runner
        self.judge = judge
        self.max_stdio_length = max_stdio_length

    async def execute(
        self,
        code: str,
        language: Language,
        execution_cases: list[ExecutionCase],
    ) -> list[ExecutionCase]:
        if not execution_cases:
            return []

        logger.info(
            "runner-call",
            extra={
                "extra": {
                    "language": language.value,
                    "execution_cases_count": len(execution_cases),
                }
            },
        )

        try:
            runner_results = await self.runner.run(
                code=code,
                language=language,
                execution_cases=execution_cases,
            )

        except Exception as exc:
            logger.exception(
                "runner_failed",
                extra={
                    "extra": {
                        "language": language.value,
                        "execution_cases_count": len(execution_cases),
                    }
                },
            )
            raise ExecutionError(
                message="Execution failed",
                details={
                    "stage": "runner",
                    "language": language.value,
                    "execution_cases_count": len(execution_cases),
                },
            ) from exc

        if len(runner_results) != len(execution_cases):
            raise ExecutionContractError(
                message="Runner returned incorrect number of results",
                details={
                    "expected": len(execution_cases),
                    "actual": len(runner_results),
                },
            )

        logger.info(
            "runner_completed",
            extra={
                "extra": {
                    "execution_cases_count": len(execution_cases),
                },
            },
        )

        execution_case_map = {
            execution_case.id: execution_case for execution_case in execution_cases
        }
        seen_ids = set()

        for runner_result in runner_results:
            if runner_result.execution_case_id in seen_ids:
                raise ExecutionContractError(
                    message="Duplicate ExecutionCase id",
                    details={
                        "execution_case_id": runner_result.execution_case_id,
                        "reason": "duplicate_id",
                    },
                )

            seen_ids.add(runner_result.execution_case_id)
            execution_case = execution_case_map.get(runner_result.execution_case_id)

            if execution_case is None:
                raise ExecutionContractError(
                    message="Unknown ExecutionCase id",
                    details={
                        "execution_case_id": runner_result.execution_case_id,
                        "reason": "unknown_execution_case",
                    },
                )

            try:
                request = JudgeRequestFactory.create_request(
                    execution_case=execution_case, runner_result=runner_result
                )
                status = self.judge.evaluate(request=request)

            except Exception as exc:
                logger.exception(
                    "judge_failed",
                    extra={
                        "extra": {
                            "check_type": request.check_type.value,
                        }
                    },
                )
                raise ExecutionError(
                    message="Execution failed",
                    details={
                        "stage": "judge",
                        "check_type": request.check_type.value,
                    },
                ) from exc

            execution_case.apply_result(
                status=status,
                stdout=self._truncate(runner_result.stdout),
                stderr=self._truncate(runner_result.stderr),
                execution_time_ms=runner_result.execution_time_ms,
            )

        return execution_cases

    @staticmethod
    def count_passed_tests(execution_cases: list[ExecutionCase]) -> int:
        return sum(
            1
            for execution_case in execution_cases
            if execution_case.status == ExecutionStatus.PASSED
        )

    @staticmethod
    def summarize(
        execution_cases: list[ExecutionCase],
    ) -> tuple[PreviewEvaluationStatus, ExecutionCase | None]:
        errors = []
        wrong = []

        for execution_case in execution_cases:
            if execution_case.status in ExecutionStatus.get_error_statuses():
                errors.append(execution_case)
            elif execution_case.status == ExecutionStatus.WRONG_ANSWER:
                wrong.append(execution_case)

        if errors:
            return PreviewEvaluationStatus.ERROR, errors[0]

        if wrong:
            return PreviewEvaluationStatus.WRONG_ANSWER, wrong[0]

        return PreviewEvaluationStatus.OK, None

    def _truncate(self, value: str) -> str:
        if len(value) <= self.max_stdio_length:
            return value

        suffix = "...<truncated>"
        max_len = max(self.max_stdio_length - len(suffix), 0)
        return value[:max_len] + suffix
