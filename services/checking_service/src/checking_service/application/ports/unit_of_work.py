from typing import Protocol

from checking_service.application.ports.repositories import (
    EvaluationRepository,
    ExecutionCaseRepository,
    InputCaseRepository,
    OutboxRepository,
)


class UnitOfWork(Protocol):
    evaluation_repo: EvaluationRepository
    execution_case_repo: ExecutionCaseRepository
    input_case_repo: InputCaseRepository
    outbox_repo: OutboxRepository

    async def __aenter__(self) -> "UnitOfWork": ...
    async def __aexit__(self, exc_type, exc, tb): ...
    async def commit(self) -> None: ...
    async def rollback(self) -> None: ...
