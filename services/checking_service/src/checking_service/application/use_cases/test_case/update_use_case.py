from uuid import UUID

from checking_service.domain.errors import DomainError
from checking_service.application.dto.test_case import TestCaseDTO, UpdateTestCaseDTO
from checking_service.application.dto.mappers import TestCaseMapper
from checking_service.application.ports import UnitOfWork
from checking_service.application.errors import (
    ApplicationError,
    NotFoundError,
    InternalError,
    ValidationError,
)


class UpdateTestCaseUseCase:
    def __init__(self, uow: UnitOfWork) -> None:
        self.uow = uow

    async def execute(self, id: UUID, dto: UpdateTestCaseDTO) -> TestCaseDTO:
        try:
            async with self.uow as uow:
                domain = await uow.test_case_repo.get(id=id)

                if domain is None:
                    raise NotFoundError(
                        message="TestCase not found",
                        details={
                            "entity": "test_case",
                            "id": id,
                        },
                    )

                updating_domain = TestCaseMapper.apply_update(
                    domain=domain, update_dto=dto
                )
                result_domain = await uow.test_case_repo.update(
                    test_case=updating_domain
                )
                await uow.commit()

            return TestCaseMapper.to_dto(domain=result_domain)

        except DomainError as exc:
            raise ValidationError(
                message=exc.message,
                details=exc.details,
            ) from exc

        except ApplicationError:
            raise

        except Exception as exc:
            raise InternalError(
                message="Failed to update TestCase",
                details={
                    "entity": "test_case",
                    "id": id,
                },
            ) from exc
