from fastapi import APIRouter

from task_service.presentation.api.routes.assignments_route import assignment_route
from task_service.presentation.api.routes.group_assignments_route import (
    group_assignment_route,
)
from task_service.presentation.api.routes.submissions_route import submission_route
from task_service.presentation.api.routes.final_results_route import final_result_route


main_router = APIRouter(prefix="/api/v1")
main_router.include_router(router=assignment_route)
main_router.include_router(router=group_assignment_route)
main_router.include_router(router=submission_route)
main_router.include_router(router=final_result_route)


__all__ = ("main_router",)
