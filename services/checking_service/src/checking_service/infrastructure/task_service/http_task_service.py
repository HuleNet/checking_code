from httpx import AsyncClient

from checking_service.application.dto.evaluation import EvaluationDTO


class HTTPTaskService:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")

    async def complete_submission(self, dto: EvaluationDTO) -> None:
        async with AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/api/v1/internal/submissions/complete",
                json={
                    "id": str(dto.id),
                    "submission_id": str(dto.submission_id),
                    "tests_total": dto.tests_total,
                    "tests_passed": dto.tests_passed,
                },
                timeout=15,
            )
            response.raise_for_status()
