from uuid import UUID

from fastapi import APIRouter, Query, status

from task_service.application.models.pagination import CursorPagination
from task_service.infrastructure.bootstrap import container
from task_service.presentation.schemas.pagination import PageResponse
from task_service.presentation.schemas.submission import (
    SubmissionResponse,
    CreateSubmissionRequest,
)


submission_router = APIRouter(prefix="/submissions", tags=["Submissions"])


@submission_router.post(
    "/",
    response_model=SubmissionResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_submission(
    payload: CreateSubmissionRequest,
) -> SubmissionResponse:
    result = await container.use_cases.create_submission.execute(dto=payload.to_dto())
    return SubmissionResponse.model_validate(result)


@submission_router.get(
    "/{id}",
    response_model=SubmissionResponse,
    status_code=status.HTTP_200_OK,
)
async def get_submission(id: UUID) -> SubmissionResponse:
    result = await container.use_cases.get_submission.execute(id=id)
    return SubmissionResponse.model_validate(result)


@submission_router.get(
    "group-assignment/{group_assignment_id}/page",
    response_model=PageResponse[SubmissionResponse],
    status_code=status.HTTP_200_OK,
)
async def get_submission_page(
    group_assignment_id: UUID,
    limit: int = Query(default=20, ge=1, le=100),
    cursor: UUID | None = Query(default=None),
) -> PageResponse[SubmissionResponse]:
    pagination = CursorPagination(
        limit=limit,
        cursor={"id": cursor} if cursor else None,
    )
    results = await container.use_cases.get_submission_page.execute(
        group_assignment_id=group_assignment_id,
        pagination=pagination,
    )
    return PageResponse(
        items=[SubmissionResponse.model_validate(result) for result in results.items],
        next_cursor=results.next_cursor,
    )


@submission_router.get(
    "student/{student_id}/group-assignment/{group_assignment_id}/page",
    response_model=PageResponse[SubmissionResponse],
    status_code=status.HTTP_200_OK,
)
async def get_submission_page_to_student(
    student_id: UUID,
    group_assignment_id: UUID,
    limit: int = Query(default=20, ge=1, le=100),
    cursor: UUID | None = Query(default=None),
) -> PageResponse[SubmissionResponse]:
    pagination = CursorPagination(
        limit=limit,
        cursor={"id": cursor} if cursor else None,
    )
    results = await container.use_cases.get_submission_page_to_student.execute(
        student_id=student_id,
        group_assignment_id=group_assignment_id,
        pagination=pagination,
    )
    return PageResponse(
        items=[SubmissionResponse.model_validate(result) for result in results.items],
        next_cursor=results.next_cursor,
    )


@submission_router.delete(
    "/{id}",
    response_model=SubmissionResponse,
    status_code=status.HTTP_200_OK,
)
async def delete_submission(id: UUID) -> SubmissionResponse:
    result = await container.use_cases.delete_submission.execute(id=id)
    return SubmissionResponse.model_validate(result)
