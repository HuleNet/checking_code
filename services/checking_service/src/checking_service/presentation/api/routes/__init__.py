from fastapi import APIRouter

from checking_service.presentation.api.routes.test_cases_route import test_case_router
from checking_service.presentation.api.routes.evaluations_route import evaluation_router
from checking_service.presentation.api.routes.execution_cases_route import (
    execution_case_router,
)


main_router = APIRouter(prefix="/api/v1")
main_router.include_router(router=test_case_router)
main_router.include_router(router=evaluation_router)
main_router.include_router(router=execution_case_router)


__all__ = ("main_router",)
