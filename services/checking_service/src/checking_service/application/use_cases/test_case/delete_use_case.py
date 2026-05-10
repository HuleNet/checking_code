from uuid import UUID

from checking_service.domain.errors import DomainError
from checking_service.application.dto.test_case import TestCaseDTO
from checking_service.application.dto.mappers import TestCaseMapper
from checking_service.application.ports import UnitOfWork
from checking_service.application.errors import (
    ApplicationError,
    NotFoundError,
    InternalError,
    ValidationError,
)


class DeleteTestCaseUseCase:
    def __init__(self, uow: UnitOfWork) -> None:
        self.uow = uow

    async def execute(self, id: UUID) -> TestCaseDTO:
        try:
            async with self.uow as uow:
                domain_result = await uow.test_case_repo.delete(id=id)

                if domain_result is None:
                    raise NotFoundError(
                        message="TestCase not found",
                        details={
                            "entity": "test_case",
                            "id": id,
                        },
                    )

                await uow.commit()

            return TestCaseMapper.to_dto(domain=domain_result)

        except DomainError as exc:
            raise ValidationError(
                message=exc.message,
                details=exc.details,
            ) from exc

        except ApplicationError:
            raise

        except Exception as exc:
            raise InternalError(
                message="Failed to delete TestCase",
                details={
                    "entity": "test_case",
                    "id": id,
                },
            ) from exc
