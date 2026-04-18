from checking_service.domain.entities import ExecutionCase
from checking_service.application.dto.execution_case import ExecutionCaseDTO


class ExecutionCaseMapper:
    @staticmethod
    def to_dto(domain: ExecutionCase) -> ExecutionCaseDTO:
        return ExecutionCaseDTO(
            id=domain.id,
            evaluation_id=domain.evaluation_id,
            input_data=domain.input_data,
            expected_output=domain.expected_output,
            check_type=domain.check_type.value,
            status=domain.status.value if domain.status else None,
            stdout=domain.stdout,
            stderr=domain.stderr,
            execution_time_ms=domain.execution_time_ms,
        )
