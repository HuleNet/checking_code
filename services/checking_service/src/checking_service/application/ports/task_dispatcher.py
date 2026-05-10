from typing import Protocol


class TaskDispatcher(Protocol):
    async def dispatch(self, task_name: str, payload: dict) -> None: ...
