from dataclasses import dataclass

from checking_service.domain.enums import CheckType


@dataclass(frozen=True)
class JudgeRequest:
    expected: str
    stdout: str
    stderr: str
    check_type: CheckType
    exit_code: int
    timeout: bool
    memory_exceeded: bool
