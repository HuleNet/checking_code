from uuid import UUID

from httpx import AsyncClient, Timeout

from task_service.application.dto.evaluation import EvaluationDTO
from task_service.application.ports import CheckingService


class HTTPCheckingService(CheckingService):
    def __init__(self, base_url: str, timeout: float = 30.0) -> None:
        self.base_url = base_url
        self.timeout = timeout

    async def start_evaluation(
        self,
        submission_id: UUID,
        assignment_id: UUID,
        language: str,
        code: str,
    ) -> EvaluationDTO:
        async with AsyncClient(timeout=Timeout(self.timeout)) as client:
            response = await client.post(
                f"{self.base_url}/evaluations/start",
                json={
                    "submission_id": str(submission_id),
                    "assignment_id": str(assignment_id),
                    "language": language,
                    "code": code,
                },
            )
            response.raise_for_status()
            payload = response.json()

        return EvaluationDTO(
            id=payload["id"],
            status=payload["status"],
        )

    async def get_evaluation(self, evaluation_id: str) -> EvaluationDTO:
        async with AsyncClient(timeout=Timeout(self.timeout)) as client:
            response = await client.get(
                f"{self.base_url}/evaluations/{evaluation_id}",
            )
            response.raise_for_status()
            payload = response.json()

        return EvaluationDTO(
            id=payload["id"],
            status=payload["status"],
            tests_passed=payload["passed_tests_count"],
            tests_total=payload["total_tests_count"],
        )
