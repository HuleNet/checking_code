from checking_service.domain.value_objects import (
    CheckType,
    EvaluationStatus,
    EvaluationResult,
)
from checking_service.domain.entities import ExecutionCase


class JudgeService:
    def __init__(self, epsilon: float) -> None:
        self.epsilon = epsilon
        self._comparators = {
            CheckType.EXACT_MATCH: self._compare_exact,
            CheckType.IGNORE_WHITESPACE: self._compare_ignore_whitespace,
            CheckType.LINE_BY_LINE: self._compare_line_by_line,
            CheckType.FLOAT_COMPARE: self._compare_float,
        }

    def evaluate(self, execution_cases: list[ExecutionCase]) -> EvaluationResult:
        tests_passed = 0
        has_error = False
        has_failed = False

        for execution_case in execution_cases:
            if execution_case.exit_code != 0 or execution_case.stderr:
                has_error = True
                continue

            comparator = self._comparators.get(execution_case.check_type)

            if comparator is None:
                has_error = True
                continue

            is_passed = comparator(
                expected=(execution_case.expected_output),
                actual=(execution_case.stdout or ""),
            )

            if is_passed:
                tests_passed += 1

            else:
                has_failed = True

        if has_error:
            return EvaluationResult(
                status=EvaluationStatus.ERROR,
                tests_passed=tests_passed,
            )

        if has_failed:
            return EvaluationResult(
                status=EvaluationStatus.FAILED,
                tests_passed=tests_passed,
            )

        return EvaluationResult(
            status=EvaluationStatus.PASSED,
            tests_passed=tests_passed,
        )

    def _compare_exact(self, expected: str, actual: str) -> bool:
        return expected.rstrip("\n") == actual.rstrip("\n")

    def _compare_ignore_whitespace(self, expected: str, actual: str) -> bool:
        return expected.split() == actual.split()

    def _compare_line_by_line(self, expected: str, actual: str) -> bool:
        expected_lines = expected.rstrip("\n").splitlines()
        actual_lines = actual.rstrip("\n").splitlines()

        if len(expected_lines) != len(actual_lines):
            return False

        for expected_line, actual_line in zip(expected_lines, actual_lines):
            if expected_line.split() != actual_line.split():
                return False

        return True

    def _compare_float(self, expected: str, actual: str) -> bool:
        try:
            expected_values = list(map(float, expected.split()))
            actual_values = list(map(float, actual.split()))

        except ValueError:
            return False

        if len(expected_values) != len(actual_values):
            return False

        for expected_value, actual_value in zip(expected_values, actual_values):
            if abs(expected_value - actual_value) > self.epsilon:
                return False

        return True
