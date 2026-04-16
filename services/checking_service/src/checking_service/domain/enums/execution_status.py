from checking_service.domain.enums import BaseEnum


class ExecutionStatus(BaseEnum):
    PASSED = "PASSED"
    WRONG_ANSWER = "WRONG_ANSWER"
    RUNTIME_ERROR = "RUNTIME_ERROR"
    TIMEOUT = "TIMEOUT"
    MEMORY_LIMIT = "MEMORY_LIMIT"
    SYSTEM_ERROR = "SYSTEM_ERROR"

    @classmethod
    def get_error_statuses(cls) -> set["ExecutionStatus"]:
        return {
            cls.RUNTIME_ERROR,
            cls.TIMEOUT,
            cls.MEMORY_LIMIT,
            cls.SYSTEM_ERROR,
        }
