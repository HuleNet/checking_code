from uuid import UUID
from datetime import datetime

from task_service.application.dto.assignment import (
    CreateAssignmentDTO,
    UpdateAssignmentDTO,
)
from task_service.presentation.schemas.base_schema import BaseSchema


class AssignmentResponse(BaseSchema):
    id: UUID
    title: str
    description: str
    created_at: datetime


class CreateAssignmentRequest(BaseSchema):
    title: str
    description: str

    def to_dto(self) -> CreateAssignmentDTO:
        return CreateAssignmentDTO(
            title=self.title,
            description=self.description,
        )


class UpdateAssignmentRequest(BaseSchema):
    title: str | None
    description: str | None

    def to_dto(self) -> UpdateAssignmentDTO:
        return UpdateAssignmentDTO(
            title=self.title,
            description=self.description,
        )
