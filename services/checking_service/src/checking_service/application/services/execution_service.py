from checking_service.domain.enums import ExecutionStatus, Language
from checking_service.domain.entities import ExecutionCase
from checking_service.application.models.enums import PreviewEvaluationStatus
from checking_service.application.models.factories import JudgeRequestFactory
from checking_service.application.ports import Runner, Judge
from checking_service.application.errors import ApplicationError, NotFoundError


class ExecutionService:
    def __init__(self, runner: Runner, judge: Judge, max_stdio_length: int) -> None:
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

        runner_results = await self.runner.run(
            code=code,
            language=language,
            execution_cases=execution_cases,
        )

        if len(runner_results) != len(execution_cases):
            # !ДОБАВИТЬ ПОДХОДЯЩИЙ ERROR!
            raise ApplicationError(
                message="",
                details={},
            )

        execution_case_map = {
            execution_case.id: execution_case for execution_case in execution_cases
        }
        seen_ids = set()

        for runner_result in runner_results:
            if runner_result.execution_case_id in seen_ids:
                # !ДОБАВИТЬ ПОДХОДЯЩИЙ ERROR!
                raise ApplicationError(
                    message="",
                    details={},
                )

            seen_ids.add(runner_result.execution_case_id)
            execution_case = execution_case_map.get(runner_result.execution_case_id)

            if execution_case is None:
                raise NotFoundError(
                    message="ExecutionCase in runner results not found",
                    details={
                        "dry_run": True,
                        "execution_case_id": runner_result.execution_case_id,
                    },
                )

            request = JudgeRequestFactory.create_request(
                execution_case=execution_case, runner_result=runner_result
            )
            status = self.judge.evaluate(request=request)
            execution_case.apply_result(
                status=status,
                stdout=self._truncate(runner_result.stdout),
                stderr=self._truncate(runner_result.stderr),
                execution_time_ms=runner_result.execution_time_ms,
            )

        return execution_cases

    @staticmethod
    def dry_count_passed(execution_cases: list[ExecutionCase]) -> int:
        return sum(
            1
            for execution_case in execution_cases
            if execution_case.status == ExecutionStatus.PASSED
        )

    @staticmethod
    def dry_summarize(
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
