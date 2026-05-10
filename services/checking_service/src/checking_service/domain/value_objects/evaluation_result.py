from dataclasses import dataclass

from checking_service.domain.value_objects import EvaluationStatus


@dataclass(frozen=True)
class EvaluationResult:
    status: EvaluationStatus
    tests_passed: int
