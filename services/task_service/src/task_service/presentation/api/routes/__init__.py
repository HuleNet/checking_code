from fastapi import APIRouter

from task_service.presentation.api.routes.assignments_route import assignment_router
from task_service.presentation.api.routes.group_assignments_route import (
    group_assignment_router,
)
from task_service.presentation.api.routes.submissions_route import submission_router
from task_service.presentation.api.routes.final_results_route import final_result_router
from task_service.presentation.api.routes.internal_route import internal_router


main_router = APIRouter(prefix="/api/v1")
main_router.include_router(router=assignment_router)
main_router.include_router(router=group_assignment_router)
main_router.include_router(router=submission_router)
main_router.include_router(router=final_result_router)
main_router.include_router(router=internal_router)


__all__ = ("main_router",)
