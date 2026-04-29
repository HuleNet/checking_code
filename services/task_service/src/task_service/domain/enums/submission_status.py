from task_service.domain.enums import BaseEnum


class SubmissionStatus(BaseEnum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
