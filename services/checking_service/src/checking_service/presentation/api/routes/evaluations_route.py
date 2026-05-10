from uuid import UUID

from fastapi import APIRouter, Query, status

from checking_service.application.models.pagination import CursorPagination
from checking_service.infrastructure.bootstrap import container
from checking_service.presentation.schemas.pagination import PageResponse
from checking_service.presentation.schemas.evaluation import (
    EvaluationResponse,
    StartEvaluationRequest,
    PreviewEvaluationResponse,
    PreviewStartEvaluationRequest,
)


evaluation_router = APIRouter(prefix="/evaluations", tags=["Evaluations"])


@evaluation_router.post(
    "/run",
    response_model=EvaluationResponse,
    status_code=status.HTTP_201_CREATED,
)
async def run_evaluation(payload: StartEvaluationRequest) -> EvaluationResponse:
    result = await container.use_cases.create_evaluation.execute(dto=payload.to_dto())
    return EvaluationResponse.model_validate(result)


@evaluation_router.post(
    "/run",
    response_model=PreviewEvaluationResponse,
    status_code=status.HTTP_200_OK,
)
async def preview_run(
    payload: PreviewStartEvaluationRequest,
) -> PreviewEvaluationResponse:
    result = await container.use_cases.preview_run_evaluation.execute(
        dto=payload.to_dto()
    )
    return PreviewEvaluationResponse.model_validate(result)


@evaluation_router.get(
    "/{id}",
    response_model=EvaluationResponse,
    status_code=status.HTTP_200_OK,
)
async def get_evaluation(id: UUID) -> EvaluationResponse:
    result = await container.use_cases.get_evaluation.execute(id=id)
    return EvaluationResponse.model_validate(result)


@evaluation_router.get(
    "/submission/{submission_id}/page",
    response_model=PageResponse[EvaluationResponse],
    status_code=status.HTTP_200_OK,
)
async def get_evaluation_page(
    submission_id: UUID,
    limit: int = Query(default=20, ge=1, le=100),
    cursor: UUID | None = Query(default=None),
) -> PageResponse[EvaluationResponse]:
    pagination = CursorPagination(
        limit=limit,
        cursor={"id": cursor} if cursor else None,
    )
    results = await container.use_cases.get_evaluation_page.execute(
        submission_id=submission_id,
        pagination=pagination,
    )
    return PageResponse(
        items=[EvaluationResponse.model_validate(result) for result in results.items],
        next_cursor=results.next_cursor,
    )


@evaluation_router.delete(
    "/{id}",
    response_model=EvaluationResponse,
    status_code=status.HTTP_200_OK,
)
async def delete_evaluation(id: UUID) -> EvaluationResponse:
    result = await container.use_cases.delete_evaluation.execute(id=id)
    return EvaluationResponse.model_validate(result)
