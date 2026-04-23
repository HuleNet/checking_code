from fastapi import APIRouter

from checking_service.presentation.api.input_cases_route import input_case_router
from checking_service.presentation.api.evaluations_route import evaluation_router
from checking_service.presentation.api.execution_cases_route import (
    execution_case_router,
)
from checking_service.presentation.api.preview_run_route import preview_run_router


main_router = APIRouter(prefix="/api/v1")
main_router.include_router(router=input_case_router)
main_router.include_router(router=evaluation_router)
main_router.include_router(router=execution_case_router)
main_router.include_router(router=preview_run_router)
