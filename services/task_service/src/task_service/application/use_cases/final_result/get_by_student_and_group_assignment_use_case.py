from uuid import UUID

from task_service.domain.errors import DomainError
from task_service.application.dto.final_result import FinalResultDTO
from task_service.application.dto.mappers import FinalResultMapper
from task_service.application.ports import UnitOfWork
from task_service.application.errors import (
    ApplicationError,
    NotFoundError,
    InternalError,
    ValidationError,
)


class GetFinalResultByStudentAndGroupAssignmentUseCase:
    def __init__(self, uow: UnitOfWork) -> None:
        self.uow = uow

    async def execute(
        self, student_id: UUID, group_assignment_id: UUID
    ) -> FinalResultDTO:
        try:
            async with self.uow as uow:
                domain_result = (
                    await uow.final_result_repo.get_by_student_and_group_assignment(
                        student_id=student_id,
                        group_assignment_id=group_assignment_id,
                    )
                )

            if domain_result is None:
                raise NotFoundError(
                    message="FinalResult not found",
                    details={
                        "entity": "final_result",
                        "student_id": student_id,
                        "group_assignment_id": group_assignment_id,
                    },
                )

            return FinalResultMapper.to_dto(domain=domain_result)

        except DomainError as exc:
            raise ValidationError(
                message=exc.message,
                details=exc.details,
            ) from exc

        except ApplicationError:
            raise

        except Exception as exc:
            raise InternalError(
                message="Failed to get FinalResult",
                details={
                    "entity": "final_result",
                    "student_id": student_id,
                    "group_assignment_id": group_assignment_id,
                },
            ) from exc
