from checking_service.domain.enums import CheckType
from checking_service.domain.entities import InputCase
from checking_service.application.dto.input_case import InputCaseDTO, UpdateInputCaseDTO
from checking_service.application.errors import ValidationError


class InputCaseMapper:
    @staticmethod
    def to_domain(dto: InputCaseDTO) -> InputCase:
        try:
            return InputCase(
                id=dto.id,
                assignment_id=dto.assignment_id,
                input_data=dto.input_data,
                expected_output=dto.expected_output,
                check_type=CheckType(dto.check_type),
            )

        except ValueError:
            raise ValidationError(
                message="Unsupported check type",
                details={
                    "check_type": dto.check_type,
                },
            )

    @staticmethod
    def to_dto(domain: InputCase) -> InputCaseDTO:
        return InputCaseDTO(
            id=domain.id,
            assignment_id=domain.assignment_id,
            input_data=domain.input_data,
            expected_output=domain.expected_output,
            check_type=domain.check_type.value,
        )

    @staticmethod
    def apply_update(domain: InputCase, update_dto: UpdateInputCaseDTO) -> InputCase:
        try:
            return InputCase(
                id=domain.id,
                assignment_id=domain.assignment_id,
                input_data=update_dto.input_data
                if update_dto.input_data
                else domain.input_data,
                expected_output=update_dto.expected_output
                if update_dto.expected_output
                else domain.expected_output,
                check_type=CheckType(update_dto.check_type)
                if update_dto.check_type
                else domain.check_type,
            )

        except ValueError:
            raise ValidationError(
                message="Unsupported check type",
                details={
                    "check_type": update_dto.check_type,
                },
            )
