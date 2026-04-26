from task_service.domain.enums import BaseEnum


class SubmissionStatus(BaseEnum):
    CREATED = "CREATED"
    CHECKING = "CHECKING"
    DONE = "DONE"
    FAILED = "FAILED"
