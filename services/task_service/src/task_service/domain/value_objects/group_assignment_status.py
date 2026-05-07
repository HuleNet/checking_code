from task_service.domain.value_objects import BaseEnum


class GroupAssignmentStatus(BaseEnum):
    ACTIVE = "ACTIVE"
    FINALIZING = "FINALIZING"
    FINALIZED = "FINALIZED"
