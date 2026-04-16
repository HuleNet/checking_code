from checking_service.domain.enums import BaseEnum


class EvaluationStatus(BaseEnum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    PASSED = "PASSED"
    FAILED = "FAILED"
    ERROR = "ERROR"

    @classmethod
    def get_finish_statuses(cls) -> set["EvaluationStatus"]:
        return {cls.PASSED, cls.FAILED, cls.ERROR}
