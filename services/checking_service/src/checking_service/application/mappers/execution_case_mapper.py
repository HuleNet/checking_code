from checking_service.domain.enums import ExecutionStatus
from checking_service.domain.entities import ExecutionCase
from checking_service.application.dto.execution_case import ExecutionCaseDTO
from checking_service.application.errors import ValidationError


class ExecutionCaseMapper:
    @staticmethod
    def to_domain(dto: ExecutionCaseDTO) -> ExecutionCase:
        try:
            return ExecutionCase(
                id=dto.id,
                evaluation_id=dto.evaluation_id,
                input_case_id=dto.input_case_id,
                status=ExecutionStatus(dto.status),
                stdout=dto.stdout,
                stderr=dto.stderr,
                execution_time_ms=dto.execution_time_ms,
            )

        except ValueError:
            raise ValidationError(
                message="Unsupported execution status",
                details={
                    "execution_status": dto.status,
                },
            )

    @staticmethod
    def to_dto(domain: ExecutionCase) -> ExecutionCaseDTO:
        return ExecutionCaseDTO(
            id=domain.id,
            evaluation_id=domain.evaluation_id,
            input_case_id=domain.input_case_id,
            status=domain.status.value,
            stdout=domain.stdout,
            stderr=domain.stderr,
            execution_time_ms=domain.execution_time_ms,
        )
