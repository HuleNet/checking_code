from typing import Protocol, Any

from checking_service.application.ports.repositories import (
    EvaluationRepository,
    ExecutionCaseRepository,
    TestCaseRepository,
    OutboxRepository,
)


class UnitOfWork(Protocol):
    evaluation_repo: EvaluationRepository
    execution_case_repo: ExecutionCaseRepository
    test_case_repo: TestCaseRepository
    outbox_repo: OutboxRepository

    async def __aenter__(self) -> "UnitOfWork": ...

    async def __aexit__(self, exc_type, exc, tb): ...

    async def commit(self) -> None: ...

    async def rollback(self) -> None: ...

    async def track(self, entity: Any) -> None: ...
