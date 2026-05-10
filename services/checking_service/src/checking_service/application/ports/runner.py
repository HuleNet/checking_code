from typing import Protocol

from checking_service.domain.value_objects import Language
from checking_service.domain.entities import ExecutionCase
from checking_service.application.dto.execution_case import ExecutionCaseResultDTO


class Runner(Protocol):
    async def run(
        self, code: str, language: Language, execution_cases: list[ExecutionCase]
    ) -> list[ExecutionCaseResultDTO]: ...
