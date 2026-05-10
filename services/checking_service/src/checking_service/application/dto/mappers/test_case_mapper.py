from uuid import UUID

from checking_service.domain.entities import TestCase
from checking_service.application.dto.test_case import (
    TestCaseDTO,
    CreateTestCaseDTO,
    UpdateTestCaseDTO,
)
from checking_service.application.dto.mappers import DomainEnumsMapper


class TestCaseMapper:
    @staticmethod
    def to_domain(dto: CreateTestCaseDTO, id: UUID) -> TestCase:
        check_type = DomainEnumsMapper.map_check_type(check_type=dto.check_type)
        return TestCase(
            id=id,
            assignment_id=dto.assignment_id,
            input_data=dto.input_data,
            expected_output=dto.expected_output,
            check_type=check_type,
        )

    @staticmethod
    def to_dto(domain: TestCase) -> TestCaseDTO:
        return TestCaseDTO(
            id=domain.id,
            assignment_id=domain.assignment_id,
            input_data=domain.input_data,
            expected_output=domain.expected_output,
            check_type=domain.check_type,
        )

    @staticmethod
    def apply_update(domain: TestCase, update_dto: UpdateTestCaseDTO) -> TestCase:
        if update_dto.check_type:
            check_type = DomainEnumsMapper.map_check_type(
                check_type=update_dto.check_type
            )
        else:
            check_type = domain.check_type

        return TestCase(
            id=domain.id,
            assignment_id=domain.assignment_id,
            input_data=update_dto.input_data
            if update_dto.input_data is not None
            else domain.input_data,
            expected_output=update_dto.expected_output
            if update_dto.expected_output is not None
            else domain.expected_output,
            check_type=check_type,
        )
