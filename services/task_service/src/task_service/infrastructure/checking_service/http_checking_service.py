from uuid import UUID

from httpx import AsyncClient


class HTTPCheckingService:
    def __init__(self, base_url: str) -> None:
        self.base_url = base_url.rstrip("/")

    async def create_evaluation(
        self,
        submission_id: UUID,
        assignment_id: UUID,
        code: str,
        language: str,
    ) -> None:
        async with AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/api/v1/internal/evaluations/run",
                json={
                    "submission_id": str(submission_id),
                    "assignment_id": str(assignment_id),
                    "code": code,
                    "language": language,
                },
                timeout=15,
            )
            print("STATUS:", response.status_code)
            print("BODY:", response.text)
            response.raise_for_status()
