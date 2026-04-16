from uuid import uuid4

from pytest import raises

from checking_service.domain.enums import Language
from checking_service.domain.entities import Submission
from checking_service.domain.errors import InvariantViolationError


def test_submission_invariant_violation():
    with raises(InvariantViolationError):
        Submission(
            id=uuid4(),
            assignment_id=uuid4(),
            language=Language.PYTHON,
            code="",
        )
