from checking_service.domain.enums import ExecutionStatus, CheckType
from checking_service.application.models.judge_request import JudgeRequest
from checking_service.application.errors import JudgeCompareError


class JudgeService:
    def __init__(self, epsilon: float) -> None:
        self.epsilon = epsilon
        self._comparators = {
            CheckType.EXACT_MATCH: self._compare_exact,
            CheckType.IGNORE_WHITESPACE: self._compare_ignore_whitespace,
            CheckType.LINE_BY_LINE: self._compare_line_by_line,
            CheckType.FLOAT_COMPARE: self._compare_float,
        }

    def evaluate(self, request: JudgeRequest) -> ExecutionStatus:
        if request.timeout:
            return ExecutionStatus.TIMEOUT

        if request.memory_exceeded:
            return ExecutionStatus.MEMORY_LIMIT

        comparator = self._comparators.get(request.check_type)
        if comparator is None:
            return ExecutionStatus.SYSTEM_ERROR

        return comparator(expected=request.expected, actual=request.stdout)

    def _compare_exact(self, expected: str, actual: str) -> ExecutionStatus:
        if expected != actual:
            return ExecutionStatus.WRONG_ANSWER

        return ExecutionStatus.PASSED

    def _compare_ignore_whitespace(self, expected: str, actual: str) -> ExecutionStatus:
        expected_normalized = expected.strip().split()
        actual_normalized = actual.strip().split()

        if expected_normalized != actual_normalized:
            return ExecutionStatus.WRONG_ANSWER

        return ExecutionStatus.PASSED

    def _compare_line_by_line(self, expected: str, actual: str) -> ExecutionStatus:
        expected_lines = expected.strip().splitlines()
        actual_lines = actual.strip().splitlines()

        if len(expected_lines) != len(actual_lines):
            return ExecutionStatus.WRONG_ANSWER

        for e, a in zip(expected_lines, actual_lines):
            if e.split() != a.split():
                return ExecutionStatus.WRONG_ANSWER

        return ExecutionStatus.PASSED

    def _compare_float(self, expected: str, actual: str) -> ExecutionStatus:
        try:
            expected_mapped = map(float, expected.strip().split())  # type: ignore
            actual_mapped = map(float, actual.strip().split())  # type: ignore

        except ValueError:
            raise JudgeCompareError(
                message="Can't map to float",
                details={
                    "check_type": CheckType.FLOAT_COMPARE.value,
                    "expected": expected,
                    "actual": actual,
                },
            )

        for e, a in zip(expected_mapped, actual_mapped):
            if abs(e - a) > self.epsilon:
                return ExecutionStatus.WRONG_ANSWER

        return ExecutionStatus.PASSED
