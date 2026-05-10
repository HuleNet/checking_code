from uuid import UUID

from fastapi import APIRouter, Query, status

from checking_service.application.models.pagination import CursorPagination
from checking_service.infrastructure.bootstrap import container
from checking_service.presentation.schemas.pagination import PageResponse
from checking_service.presentation.schemas.execution_case import ExecutionCaseResponse

execution_case_router = APIRouter(prefix="/execution-cases", tags=["Execution Case"])


@execution_case_router.get(
    "/{id}",
    response_model=ExecutionCaseResponse,
    status_code=status.HTTP_200_OK,
)
async def get_execution_case(id: UUID) -> ExecutionCaseResponse:
    result = await container.use_cases.get_execution_case.execute(id=id)
    return ExecutionCaseResponse.model_validate(result)


@execution_case_router.get(
    "/evaluation/{evaluation_id}/page",
    response_model=PageResponse[ExecutionCaseResponse],
    status_code=status.HTTP_200_OK,
)
async def get_execution_case_page(
    evaluation_id: UUID,
    limit: int = Query(default=20, ge=1, le=100),
    cursor: UUID | None = Query(default=None),
) -> PageResponse[ExecutionCaseResponse]:
    pagination = CursorPagination(
        limit=limit,
        cursor={"id": cursor} if cursor else None,
    )
    results = await container.use_cases.get_execution_case_page.execute(
        evaluation_id=evaluation_id, pagination=pagination
    )
    return PageResponse(
        items=[
            ExecutionCaseResponse.model_validate(result) for result in results.items
        ],
        next_cursor=results.next_cursor,
    )
