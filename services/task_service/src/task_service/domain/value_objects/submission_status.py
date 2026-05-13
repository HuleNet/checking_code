from task_service.domain.value_objects import BaseEnum


class SubmissionStatus(BaseEnum):
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
