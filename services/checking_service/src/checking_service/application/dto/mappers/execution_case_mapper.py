from uuid import UUID

from checking_service.domain.entities import ExecutionCase, TestCase
from checking_service.application.dto.execution_case import ExecutionCaseDTO


class ExecutionCaseMapper:
    @staticmethod
    def to_domain(id: UUID, evaluation_id: UUID, test_case: TestCase) -> ExecutionCase:
        return ExecutionCase(
            id=id,
            evaluation_id=evaluation_id,
            input_data=test_case.input_data,
            expected_output=test_case.expected_output,
            check_type=test_case.check_type,
        )

    @staticmethod
    def to_dto(domain: ExecutionCase) -> ExecutionCaseDTO:
        return ExecutionCaseDTO(
            id=domain.id,
            evaluation_id=domain.evaluation_id,
            input_data=domain.input_data,
            expected_output=domain.expected_output,
            check_type=domain.check_type.value,
            stdout=domain.stdout,
            stderr=domain.stderr,
            execution_time_ms=domain.execution_time_ms,
            exit_code=domain.exit_code,
        )
