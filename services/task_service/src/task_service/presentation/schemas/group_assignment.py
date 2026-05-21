from uuid import UUID
from datetime import datetime

from task_service.application.dto.group_assignment import CreateGroupAssignmentDTO, UpdateGroupAssignmentDTO
from task_service.presentation.schemas.base_schema import BaseSchema


class GroupAssignmentResponse(BaseSchema):
    id: UUID
    group_id: UUID
    assignment_id: UUID
    allowed_languages: set[str]
    deadline: datetime
    status: str
    finalized_at: datetime | None


class CreateGroupAssignmentRequest(BaseSchema):
    group_id: UUID
    assignment_id: UUID
    allowed_languages: set[str]
    deadline: datetime

    def to_dto(self) -> CreateGroupAssignmentDTO:
        return CreateGroupAssignmentDTO(
            group_id=self.group_id,
            assignment_id=self.assignment_id,
            allowed_languages=self.allowed_languages,
            deadline=self.deadline,
        )

class UpdateGroupAssignmentRequest(BaseSchema):
    group_id: UUID | None
    assignment_id: UUID | None
    allowed_languages: set[str] | None
    deadline: datetime | None 
    
    def to_dto(self) -> UpdateGroupAssignmentDTO:
        return UpdateGroupAssignmentDTO(
            group_id=self.group_id,
            assignment_id=self.assignment_id,
            allowed_languages=self.allowed_languages,
            deadline=self.deadline,
        )           
