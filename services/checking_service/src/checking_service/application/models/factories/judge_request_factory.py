from checking_service.domain.entities import ExecutionCase
from checking_service.application.models.runner_result import RunnerResult
from checking_service.application.models.judge_request import JudgeRequest


class JudgeRequestFactory:
    @staticmethod
    def create_request(
        execution_case: ExecutionCase, runner_result: RunnerResult
    ) -> JudgeRequest:
        return JudgeRequest(
            expected=execution_case.expected_output,
            stdout=runner_result.stdout,
            stderr=runner_result.stderr,
            check_type=execution_case.check_type,
            exit_code=runner_result.exit_code,
            timeout=runner_result.timeout,
            memory_exceeded=runner_result.memory_exceeded,
        )
