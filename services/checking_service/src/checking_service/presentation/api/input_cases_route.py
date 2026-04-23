from uuid import UUID
from typing import Annotated

from fastapi import APIRouter, Depends, status

from checking_service.application.use_cases.input_case import (
    CreateInputCaseUseCase,
    GetInputCaseUseCase,
    GetInputCasesByAssignmentUseCase,
    GetInputCasePageUseCase,
    UpdateInputCaseUseCase,
    DeleteInputCaseUseCase,
)
from checking_service.presentation.schemas import (
    InputCaseResponse,
    CreateInputCaseRequest,
    UpdateInputCaseRequest,
)
from checking_service.presentation.dependencies.input_case_use_cases import (
    get_use_case_create_input_case,
    get_use_case_get_input_case,
    get_use_case_get_by_assignment_input_case,
    get_use_case_get_input_case_page,
    get_ues_case_update_input_case,
    get_use_case_delete_input_case,
)


input_case_router = APIRouter(prefix="/input-cases", tags=["Input Cases"])


@input_case_router.post(
    "/", response_model=InputCaseResponse, status_code=status.HTTP_201_CREATED
)
async def create_input_case(
    payload: CreateInputCaseRequest,
    use_case: Annotated[
        CreateInputCaseUseCase, Depends(get_use_case_create_input_case)
    ],
) -> InputCaseResponse:
    result = await use_case.execute(dto=payload.to_dto())
    return InputCaseResponse.model_validate(result)


@input_case_router.get(
    "/{id}", response_model=InputCaseResponse, status_code=status.HTTP_200_OK
)
async def get_input_case(
    id: UUID,
    use_case: Annotated[GetInputCaseUseCase, Depends(get_use_case_get_input_case)],
) -> InputCaseResponse:
    result = await use_case.execute(id=id)
    return InputCaseResponse.model_validate(result)


@input_case_router.get(
    "/assignment/{assignment_id}",
    response_model=list[InputCaseResponse],
    status_code=status.HTTP_200_OK,
)
async def get_input_cases_by_assignment(
    assignment_id: UUID,
    use_case: Annotated[
        GetInputCasesByAssignmentUseCase,
        Depends(get_use_case_get_by_assignment_input_case),
    ],
) -> list[InputCaseResponse]:
    results = await use_case.execute(assignment_id=assignment_id)
    return [InputCaseResponse.model_validate(result) for result in results]


@input_case_router.patch(
    "/{id}",
    response_model=InputCaseResponse,
    status_code=status.HTTP_200_OK,
)
async def update_input_case(
    id: UUID,
    payload: UpdateInputCaseRequest,
    use_case: Annotated[
        UpdateInputCaseUseCase, Depends(get_ues_case_update_input_case)
    ],
) -> InputCaseResponse:
    result = await use_case.execute(id=id, dto=payload.to_dto())
    return InputCaseResponse.model_validate(result)


@input_case_router.delete(
    "/{id}",
    response_model=InputCaseResponse,
    status_code=status.HTTP_200_OK,
)
async def delete_input_case(
    id: UUID,
    use_case: Annotated[
        DeleteInputCaseUseCase, Depends(get_use_case_delete_input_case)
    ],
) -> InputCaseResponse:
    result = await use_case.execute(id=id)
    return InputCaseResponse.model_validate(result)
