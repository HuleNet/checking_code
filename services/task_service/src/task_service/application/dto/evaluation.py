from dataclasses import dataclass

from task_service.domain.value_objects import EvaluationStatus


@dataclass(frozen=True)
class EvaluationDTO:
    id: str
    status: EvaluationStatus
    tests_passed: int | None = None
    tests_total: int | None = None
