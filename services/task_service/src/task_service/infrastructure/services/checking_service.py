from uuid import UUID

from httpx import AsyncClient, Timeout

from task_service.application.dto.checking import CheckingResultDTO, PreviewRunDTO
from task_service.application.ports import CheckingService


class HTTPCheckingService(CheckingService):
    def __init__(self, base_url: str, timeout: float = 30.0) -> None:
        self.base_url = base_url
        self.timeout = timeout

    async def evaluate_submission(
        self,
        submission_id: UUID,
        assignment_id: UUID,
        language: str,
        code: str,
    ) -> CheckingResultDTO:
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

        async with AsyncClient(timeout=Timeout(self.timeout)) as client:
            response = await client.get(
                f"{self.base_url}/evaluations/{payload['id']}",
            )
            response.raise_for_status()
            payload = response.json()

        return CheckingResultDTO(
            tests_passed=payload["passed_tests_count"],
            tests_total=payload["total_tests_count"],
        )

    async def preview_run(self, dto: PreviewRunDTO):
        async with AsyncClient(timeout=Timeout(self.timeout)) as client:
            response = await client.post(
                f"{self.base_url}/evaluations/start",
                json={
                    "assignment_id": str(dto.assignment_id),
                    "language": dto.language,
                    "code": dto.code,
                },
            )
            response.raise_for_status()
            payload = response.json()

        return CheckingResultDTO(
            tests_passed=payload["passed_tests_count"],
            tests_total=payload["total_tests_count"],
        )
