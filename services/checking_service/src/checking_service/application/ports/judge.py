from typing import Protocol

from checking_service.domain.enums import ExecutionStatus
from checking_service.application.models.judge_request import JudgeRequest


class Judge(Protocol):
    def evaluate(self, request: JudgeRequest) -> ExecutionStatus: ...
