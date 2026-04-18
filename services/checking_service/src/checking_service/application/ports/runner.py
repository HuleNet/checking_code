from typing import Protocol

from checking_service.domain.enums import Language
from checking_service.domain.entities import ExecutionCase
from checking_service.application.dto.runner_result import RunnerResult


class Runner(Protocol):
    async def run(
        self, code: str, language: Language, execution_cases: list[ExecutionCase]
    ) -> list[RunnerResult]: ...
