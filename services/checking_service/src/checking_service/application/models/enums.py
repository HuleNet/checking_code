from checking_service.domain.enums import BaseEnum


class PreviewEvaluationStatus(BaseEnum):
    OK = "OK"
    WRONG_ANSWER = "WRONG_ANSWER"
    ERROR = "ERROR"


class OutboxStatus(BaseEnum):
    PENDING = "PENDING"
    PUBLISHED = "PUBLISHED"
    FAILED = "FAILED"
