from checking_service.domain.value_objects import BaseEnum


class EvaluationStatus(BaseEnum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    PASSED = "PASSED"
    FAILED = "FAILED"
    TIMEOUT = "TIMEOUT"
    MEMORY_EXCEEDED = "MEMORY_EXCEEDED"
    ERROR = "ERROR"

    @classmethod
    def get_finish_statuses(cls) -> set["EvaluationStatus"]:
        return {cls.PASSED, cls.FAILED, cls.ERROR, cls.TIMEOUT, cls.MEMORY_EXCEEDED}
