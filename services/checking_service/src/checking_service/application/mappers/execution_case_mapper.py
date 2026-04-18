from uuid import UUID

from checking_service.domain.entities import ExecutionCase, InputCase
from checking_service.application.dto.execution_case import ExecutionCaseDTO


class ExecutionCaseMapper:
    @staticmethod
    def to_domain_from_input_case(
        input_case: InputCase, id: UUID, evaluation_id: UUID
    ) -> ExecutionCase:
        return ExecutionCase(
            id=id,
            evaluation_id=evaluation_id,
            input_data=input_case.input_data,
            expected_output=input_case.expected_output,
            check_type=input_case.check_type,
        )

    @staticmethod
    def to_dto(domain: ExecutionCase) -> ExecutionCaseDTO:
        return ExecutionCaseDTO(
            id=domain.id,
            evaluation_id=domain.evaluation_id,
            input_data=domain.input_data,
            expected_output=domain.expected_output,
            check_type=domain.check_type.value,
            status=domain.status,
            stdout=domain.stdout,
            stderr=domain.stderr,
            execution_time_ms=domain.execution_time_ms,
        )
