from uuid import UUID

from task_service.application.dto.submission import SubmissionDTO
from task_service.application.dto.mappers import SubmissionMapper
from task_service.application.ports import UnitOfWork
from task_service.application.errors import (
    ApplicationError,
    NotFoundError,
    InternalError,
)


class DeleteSubmissionUseCase:
    def __init__(self, uow: UnitOfWork) -> None:
        self.uow = uow

    async def execute(self, id: UUID) -> SubmissionDTO:
        try:
            async with self.uow as uow:
                domain_result = await uow.submission_repo.delete(id=id)

                if domain_result is None:
                    raise NotFoundError(
                        message="Submission not found",
                        details={
                            "entity": "submission",
                            "id": id,
                        },
                    )

                await uow.commit()

            return SubmissionMapper.to_dto(domain=domain_result)

        except ApplicationError:
            raise

        except Exception as exc:
            raise InternalError(
                message="Failed to delete Submission",
                details={
                    "entity": "submission",
                    "id": id,
                },
            ) from exc
