from uuid import UUID
from typing import Annotated

from fastapi import APIRouter, Depends, status

from checking_service.application.use_cases.execution_case import (
    GetExecutionCaseUseCase,
    GetExecutionCasesByEvaluationUseCase,
    GetExecutionCasePageUseCase,
)
from checking_service.presentation.schemas import ExecutionCaseResponse
from checking_service.presentation.dependencies.execution_case_use_cases import (
    get_use_case_get_execution_case,
    get_use_case_get_by_evaluation_execution_cases,
    get_use_case_get_execution_case_page,
)


execution_case_router = APIRouter(prefix="/execution-cases", tags=["Execution Case"])


@execution_case_router.get(
    "/{id}", response_model=ExecutionCaseResponse, status_code=status.HTTP_200_OK
)
async def get_execution_case(
    id: UUID,
    use_case: Annotated[
        GetExecutionCaseUseCase, Depends(get_use_case_get_execution_case)
    ],
) -> ExecutionCaseResponse:
    result = await use_case.execute(id=id)
    return ExecutionCaseResponse.model_validate(result)


@execution_case_router.get(
    "/evaluation/{evaluation_id}",
    response_model=list[ExecutionCaseResponse],
    status_code=status.HTTP_200_OK,
)
async def get_execution_cases_by_evaluation(
    evaluation_id: UUID,
    use_case: Annotated[
        GetExecutionCasesByEvaluationUseCase,
        Depends(get_use_case_get_by_evaluation_execution_cases),
    ],
) -> list[ExecutionCaseResponse]:
    results = await use_case.execute(evaluation_id=evaluation_id)
    return [ExecutionCaseResponse.model_validate(result) for result in results]
