from uuid import uuid4

from checking_service.domain.services import JudgeService
from checking_service.domain.errors import DomainError
from checking_service.application.dto.submission import PreviewSubmissionDTO
from checking_service.application.dto.evaluation import PreviewEvaluationDTO
from checking_service.application.dto.mappers import (
    DomainEnumsMapper,
    ExecutionCaseMapper,
)
from checking_service.application.use_cases.test_case import (
    GetTestCasesByAssignmentUseCase,
)
from checking_service.application.ports import Runner
from checking_service.application.errors import (
    ExecutionError,
    ApplicationError,
    ValidationError,
    InternalError,
)


class PreviewRunEvaluationUseCase:
    def __init__(
        self,
        judge: JudgeService,
        runner: Runner,
        get_test_cases: GetTestCasesByAssignmentUseCase,
    ) -> None:
        self.judge = judge
        self.runner = runner
        self.get_test_cases = get_test_cases

    async def execute(self, dto: PreviewSubmissionDTO) -> PreviewEvaluationDTO:
        try:
            test_cases = await self.get_test_cases.execute(
                assignment_id=dto.assignment_id
            )
            tests_total = len(test_cases)
            execution_cases = [
                ExecutionCaseMapper.to_domain(
                    id=uuid4(), evaluation_id=uuid4(), test_case=test_case
                )
                for test_case in test_cases
            ]
            language = DomainEnumsMapper.map_language(language=dto.language)
            runner_results = await self.runner.run(
                code=dto.code,
                language=language,
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
                    execution_time_ms=runner_result.execution_time_ms,
                    exit_code=runner_result.exit_code,
                    is_timeout=runner_result.is_timeout,
                    is_memory_exceeded=runner_result.is_memory_exceeded,
                )

            if len(seen_ids) != len(execution_cases):
                missing_ids = set(execution_case_map) - seen_ids
                raise ExecutionError(
                    message="Missing ExecutionCase results",
                    details={
                        "missing_execution_case_ids": [str(id_) for id_ in missing_ids],
                        "expected_count": len(execution_cases),
                        "actual_count": len(seen_ids),
                    },
                )

            judge_result = self.judge.evaluate(execution_cases=execution_cases)

            return PreviewEvaluationDTO(
                tests_total=tests_total,
                tests_passed=judge_result.tests_passed,
                status=judge_result.status.value,
            )

        except DomainError as exc:
            exc.details["is_preview_run"] = True
            raise ValidationError(
                message=exc.message,
                details=exc.details,
            ) from exc

        except ApplicationError as exc:
            exc.details["is_preview_run"] = True
            raise

        except Exception as exc:
            raise InternalError(
                message="Failed to preview run Evaluation",
                details={
                    "entity": "evaluation",
                    "is_preview_run": True,
                },
            ) from exc
