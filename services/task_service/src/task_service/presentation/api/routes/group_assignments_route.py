from uuid import UUID

from fastapi import APIRouter, Query, status

from task_service.application.models.pagination import CursorPagination
from task_service.infrastructure.bootstrap import container
from task_service.presentation.schemas.pagination import PageResponse
from task_service.presentation.schemas.group_assignment import (
    GroupAssignmentResponse,
    CreateGroupAssignmentRequest,
)


group_assignment_route = APIRouter(
    prefix="/group-assignments", tags=["Group Assignments"]
)


@group_assignment_route.post(
    "/",
    response_model=GroupAssignmentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_group_assignment(
    payload: CreateGroupAssignmentRequest,
) -> GroupAssignmentResponse:
    result = await container.use_cases.create_group_assignment.execute(
        dto=payload.to_dto()
    )
    return GroupAssignmentResponse.model_validate(result)


@group_assignment_route.get(
    "/{id}",
    response_model=GroupAssignmentResponse,
    status_code=status.HTTP_200_OK,
)
async def get_group_assignment(id: UUID) -> GroupAssignmentResponse:
    result = await container.use_cases.get_group_assignment.execute(id=id)
    return GroupAssignmentResponse.model_validate(result)


@group_assignment_route.get(
    "/page",
    response_model=PageResponse[GroupAssignmentResponse],
    status_code=status.HTTP_200_OK,
)
async def get_group_assignment_page(
    group_id: UUID,
    limit: int = Query(default=20, ge=1, le=100),
    cursor: UUID | None = Query(default=None),
) -> PageResponse[GroupAssignmentResponse]:
    pagination = CursorPagination(
        limit=limit,
        cursor={"id": cursor} if cursor else None,
    )
    results = await container.use_cases.get_group_assignment_page.execute(
        group_id=group_id,
        pagination=pagination,
    )
    return PageResponse(
        items=[
            GroupAssignmentResponse.model_validate(result) for result in results.items
        ],
        next_cursor=results.next_cursor,
    )


@group_assignment_route.delete(
    "/{id}",
    response_model=GroupAssignmentResponse,
    status_code=status.HTTP_200_OK,
)
async def delete_group_assignment(id: UUID) -> GroupAssignmentResponse:
    result = await container.use_cases.delete_group_assignment.execute(id=id)
    return GroupAssignmentResponse.model_validate(result)
