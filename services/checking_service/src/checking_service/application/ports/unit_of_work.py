from typing import Protocol

from checking_service.application.ports.repositories import (
    EvaluationRepository,
    ExecutionCaseRepository,
    TestCaseRepository,
)


class UnitOfWork(Protocol):
    evaluation_repo: EvaluationRepository
    execution_case_repo: ExecutionCaseRepository
    test_case_repo: TestCaseRepository

    async def __aenter__(self) -> "UnitOfWork": ...

    async def __aexit__(self, exc_type, exc, tb): ...

    async def commit(self) -> None: ...

    async def rollback(self) -> None: ...
