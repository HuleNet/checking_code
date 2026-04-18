from uuid import UUID

from checking_service.domain.entities import InputCase, ExecutionCase


class ExecutionCaseFactory:
    @staticmethod
    def create_execution_case(
        id: UUID, evaluation_id: UUID, input_case: InputCase
    ) -> ExecutionCase:
        return ExecutionCase(
            id=id,
            evaluation_id=evaluation_id,
            input_data=input_case.input_data,
            expected_output=input_case.expected_output,
            check_type=input_case.check_type,
        )
