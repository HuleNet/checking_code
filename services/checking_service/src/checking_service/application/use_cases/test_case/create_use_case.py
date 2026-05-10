from uuid import uuid4

from checking_service.domain.errors import DomainError
from checking_service.application.dto.test_case import CreateTestCaseDTO, TestCaseDTO
from checking_service.application.dto.mappers import TestCaseMapper
from checking_service.application.ports import UnitOfWork
from checking_service.application.errors import (
    ApplicationError,
    InternalError,
    ValidationError,
)


class CreateTestCaseUseCase:
    def __init__(
        self,
        uow: UnitOfWork,
    ) -> None:
        self.uow = uow

    async def execute(self, dto: CreateTestCaseDTO) -> TestCaseDTO:
        try:
            async with self.uow as uow:
                test_case = TestCaseMapper.to_domain(dto=dto, id=uuid4())
                domain_result = await uow.test_case_repo.add(test_case=test_case)
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
                message="Failed to create TestCase",
                details={
                    "entity": "test_case",
                },
            ) from exc
