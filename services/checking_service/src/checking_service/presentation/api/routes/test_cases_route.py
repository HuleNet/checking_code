from uuid import UUID

from fastapi import APIRouter, Query, status

from checking_service.application.models.pagination import CursorPagination
from checking_service.infrastructure.bootstrap import container
from checking_service.presentation.schemas.pagination import PageResponse
from checking_service.presentation.schemas.test_case import (
    TestCaseResponse,
    CreateTestCaseRequest,
    UpdateTestCaseRequest,
)


test_case_router = APIRouter(prefix="/test-cases", tags=["Test Cases"])


@test_case_router.post(
    "/",
    response_model=TestCaseResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_test_case(payload: CreateTestCaseRequest) -> TestCaseResponse:
    result = await container.use_cases.create_test_case.execute(dto=payload.to_dto())
    return TestCaseResponse.model_validate(result)


@test_case_router.get(
    "/{id}",
    response_model=TestCaseResponse,
    status_code=status.HTTP_200_OK,
)
async def get_test_case(id: UUID) -> TestCaseResponse:
    result = await container.use_cases.get_test_case.execute(id=id)
    return TestCaseResponse.model_validate(result)


@test_case_router.get(
    "/assignment/{assignment_id}/page",
    response_model=PageResponse[TestCaseResponse],
    status_code=status.HTTP_200_OK,
)
async def get_test_case_page(
    assignment_id: UUID,
    limit: int = Query(default=20, ge=1, le=100),
    cursor: UUID | None = Query(default=None),
) -> PageResponse[TestCaseResponse]:
    pagination = CursorPagination(
        limit=limit,
        cursor={"id": cursor} if cursor else None,
    )
    results = await container.use_cases.get_test_case_page.execute(
        assignment_id=assignment_id,
        pagination=pagination,
    )
    return PageResponse(
        items=[TestCaseResponse.model_validate(result) for result in results.items],
        next_cursor=results.next_cursor,
    )


@test_case_router.patch(
    "/{id}",
    response_model=TestCaseResponse,
    status_code=status.HTTP_200_OK,
)
async def update_test_case(
    id: UUID, payload: UpdateTestCaseRequest
) -> TestCaseResponse:
    result = await container.use_cases.update_test_case.execute(
        id=id, dto=payload.to_dto()
    )
    return TestCaseResponse.model_validate(result)


@test_case_router.delete(
    "/{id}",
    response_model=TestCaseResponse,
    status_code=status.HTTP_200_OK,
)
async def delete_test_case(id: UUID) -> TestCaseResponse:
    result = await container.use_cases.delete_test_case.execute(id=id)
    return TestCaseResponse.model_validate(result)
