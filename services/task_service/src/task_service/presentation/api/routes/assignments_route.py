from uuid import UUID

from fastapi import APIRouter, Query, status

from task_service.application.models.pagination import CursorPagination
from task_service.infrastructure.bootstrap import container
from task_service.presentation.schemas.pagination import PageResponse
from task_service.presentation.schemas.assignment import (
    AssignmentResponse,
    CreateAssignmentRequest,
    UpdateAssignmentRequest,
)


assignment_route = APIRouter(prefix="assignments", tags=["Assignments"])


@assignment_route.post(
    "/",
    response_model=AssignmentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_assignment(payload: CreateAssignmentRequest) -> AssignmentResponse:
    result = await container.use_cases.create_assignment.execute(dto=payload.to_dto())
    return AssignmentResponse.model_validate(result)


@assignment_route.get(
    "/{id}",
    response_model=AssignmentResponse,
    status_code=status.HTTP_200_OK,
)
async def get_assignment(id: UUID) -> AssignmentResponse:
    result = await container.use_cases.get_assignment.execute(id=id)
    return AssignmentResponse.model_validate(result)


@assignment_route.get(
    "/page",
    response_model=PageResponse[AssignmentResponse],
    status_code=status.HTTP_200_OK,
)
async def get_assignment_page(
    limit: int = Query(default=20, ge=1, le=100),
    cursor: UUID | None = Query(default=None),
) -> PageResponse[AssignmentResponse]:
    pagination = CursorPagination(
        limit=limit,
        cursor={"id": cursor} if cursor else None,
    )
    results = await container.use_cases.get_assignment_page.execute(
        pagination=pagination
    )
    return PageResponse(
        items=[AssignmentResponse.model_validate(result) for result in results.items],
        next_cursor=results.next_cursor,
    )


@assignment_route.patch(
    "/{id}",
    response_model=AssignmentResponse,
    status_code=status.HTTP_200_OK,
)
async def update_assignment(
    id: UUID, payload: UpdateAssignmentRequest
) -> AssignmentResponse:
    result = await container.use_cases.update_assignment.execute(
        id=id, dto=payload.to_dto()
    )
    return AssignmentResponse.model_validate(result)


@assignment_route.delete(
    "/{id}",
    response_model=AssignmentResponse,
    status_code=status.HTTP_200_OK,
)
async def delete_assignment(id: UUID) -> AssignmentResponse:
    result = await container.use_cases.delete_assignment.execute(id=id)
    return AssignmentResponse.model_validate(result)
