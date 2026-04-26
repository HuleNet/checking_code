from task_service.domain.enums import BaseEnum


class TestStatus(BaseEnum):
    OK = "OK"
    WA = "WA"
    ERROR = "ERROR"
