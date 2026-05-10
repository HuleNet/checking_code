from uuid import UUID

from fastapi import APIRouter, Query, status

from task_service.application.models.pagination import CursorPagination
from task_service.infrastructure.bootstrap import container
from task_service.presentation.schemas.pagination import PageResponse
from task_service.presentation.schemas.final_result import FinalResultResponse


final_result_route = APIRouter(prefix="/final-results", tags=["Final Results"])


@final_result_route.get(
    "/{id}",
    response_model=FinalResultResponse,
    status_code=status.HTTP_200_OK,
)
async def get_final_result(id: UUID) -> FinalResultResponse:
    result = await container.use_cases.get_final_result.execute(id=id)
    return FinalResultResponse.model_validate(result)


@final_result_route.get(
    "/page",
    response_model=PageResponse[FinalResultResponse],
    status_code=status.HTTP_200_OK,
)
async def get_final_result_page(
    group_assignment_id: UUID,
    limit: int = Query(default=20, ge=1, le=100),
    cursor: UUID | None = Query(default=None),
) -> PageResponse[FinalResultResponse]:
    pagination = CursorPagination(
        limit=limit,
        cursor={"id": cursor} if cursor else None,
    )
    results = await container.use_cases.get_final_result_page.execute(
        group_assignment_id=group_assignment_id,
        pagination=pagination,
    )
    return PageResponse(
        items=[FinalResultResponse.model_validate(result) for result in results.items],
        next_cursor=results.next_cursor,
    )


@final_result_route.delete(
    "/{id}",
    response_model=FinalResultResponse,
    status_code=status.HTTP_200_OK,
)
async def delete_final_result(id: UUID) -> FinalResultResponse:
    result = await container.use_cases.delete_final_result.execute(id=id)
    return FinalResultResponse.model_validate(result)
