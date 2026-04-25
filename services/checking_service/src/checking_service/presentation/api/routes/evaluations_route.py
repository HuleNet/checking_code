from uuid import UUID
from typing import Annotated

from fastapi import APIRouter, Depends, status, Query

from checking_service.application.models.pagination import CursorPagination
from checking_service.application.use_cases.evaluation import (
    StartEvaluationUseCase,
    GetEvaluationUseCase,
    GetEvaluationsBySubmissionUseCase,
    GetEvaluationPageUseCase,
    DeleteEvaluationUseCase,
)
from checking_service.presentation.schemas import (
    EvaluationResponse,
    StartEvaluationRequest,
    PageResponse,
)
from checking_service.presentation.dependencies.evaluation_use_cases import (
    get_use_case_start_evaluation,
    get_use_case_get_evaluation,
    get_use_case_get_by_submission_evaluations,
    get_use_case_get_evaluation_page,
    get_use_case_delete_evaluation,
)


evaluation_router = APIRouter(prefix="/evaluations", tags=["Evaluations"])


@evaluation_router.post(
    "/start", response_model=EvaluationResponse, status_code=status.HTTP_201_CREATED
)
async def start_evaluation(
    payload: StartEvaluationRequest,
    use_case: Annotated[StartEvaluationUseCase, Depends(get_use_case_start_evaluation)],
) -> EvaluationResponse:
    result = await use_case.execute(submission=payload.to_dto())
    return EvaluationResponse.model_validate(result)


@evaluation_router.get(
    "/{id}", response_model=EvaluationResponse, status_code=status.HTTP_200_OK
)
async def get_evaluation(
    id: UUID,
    use_case: Annotated[GetEvaluationUseCase, Depends(get_use_case_get_evaluation)],
) -> EvaluationResponse:
    result = await use_case.execute(id=id)
    return EvaluationResponse.model_validate(result)


@evaluation_router.get(
    "/submission/{submission_id}",
    response_model=list[EvaluationResponse],
    status_code=status.HTTP_200_OK,
)
async def get_evaluations_by_submission(
    submission_id: UUID,
    use_case: Annotated[
        GetEvaluationsBySubmissionUseCase,
        Depends(get_use_case_get_by_submission_evaluations),
    ],
) -> list[EvaluationResponse]:
    results = await use_case.execute(submission_id=submission_id)
    return [EvaluationResponse.model_validate(result) for result in results]


@evaluation_router.get(
    "/submission/{submission_id}/page",
    response_model=PageResponse[EvaluationResponse],
    status_code=status.HTTP_200_OK,
)
async def get_evaluation_page(
    submission_id: UUID,
    use_case: Annotated[
        GetEvaluationPageUseCase, Depends(get_use_case_get_evaluation_page)
    ],
    limit: int = Query(default=20, ge=1, le=100),
    cursor: UUID | None = Query(default=None),
) -> PageResponse[EvaluationResponse]:
    pagination = CursorPagination(
        limit=limit,
        cursor={"id": cursor} if cursor else None,
    )
    results = await use_case.execute(
        submission_id=submission_id,
        pagination=pagination,
    )
    return PageResponse(
        items=[EvaluationResponse.model_validate(result) for result in results.items],
        next_cursor=results.next_cursor,
    )


@evaluation_router.delete(
    "/{id}", response_model=EvaluationResponse, status_code=status.HTTP_200_OK
)
async def delete_evaluation(
    id: UUID,
    use_case: Annotated[
        DeleteEvaluationUseCase, Depends(get_use_case_delete_evaluation)
    ],
) -> EvaluationResponse:
    result = await use_case.execute(id=id)
    return EvaluationResponse.model_validate(result)
