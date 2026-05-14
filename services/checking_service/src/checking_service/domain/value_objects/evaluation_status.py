from checking_service.domain.value_objects import BaseEnum


class EvaluationStatus(BaseEnum):
    PASSED = "PASSED"
    FAILED = "FAILED"
    MEMORY_EXCEEDED = "MEMORY_EXCEEDED"
    ERROR = "ERROR"
    SYSTEM_ERROR = "SYSTEM_ERROR"
