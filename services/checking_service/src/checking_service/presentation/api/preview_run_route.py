from typing import Annotated

from fastapi import APIRouter, Depends, status

from checking_service.application.use_cases.preview_run import PreviewRunUseCase
from checking_service.presentation.schemas import PreviewRunResponse, PreviewRunRequest
from checking_service.presentation.dependencies.preview_run_use_cases import (
    get_use_case_preview_run,
)


preview_run_router = APIRouter(prefix="/preview-runs", tags=["Preview Runs"])


@preview_run_router.post(
    "/run", response_model=PreviewRunResponse, status_code=status.HTTP_200_OK
)
async def preview_run(
    payload: PreviewRunRequest,
    use_case: Annotated[PreviewRunUseCase, Depends(get_use_case_preview_run)],
) -> PreviewRunResponse:
    result = await use_case.execute(submission=payload.to_dto())
    return PreviewRunResponse.model_validate(result)
