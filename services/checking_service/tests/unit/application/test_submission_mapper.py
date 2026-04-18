from uuid import uuid4

from pytest import raises

from checking_service.domain.errors import InvariantViolationError
from checking_service.application.dto.submission import SubmissionDTO
from checking_service.application.dto.mappers.submission_mapper import SubmissionMapper
from checking_service.application.errors import ValidationError


def test_submission_mapper_validation_error():
    dto = SubmissionDTO(
        id=uuid4(),
        assignment_id=uuid4(),
        language="CPP",
        code="",
    )

    with raises(ValidationError):
        SubmissionMapper.to_domain(dto=dto)


def test_submission_mapper_invariant_violation():
    dto = SubmissionDTO(
        id=uuid4(),
        assignment_id=uuid4(),
        language="PYTHON",
        code="",
    )

    with raises(InvariantViolationError):
        SubmissionMapper.to_domain(dto=dto)
