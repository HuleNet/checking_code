from typing import Any

from checking_service.domain.entities import TestCase
from checking_service.infrastructure.db.models import TestCaseORM


class TestCaseMapper:
    @staticmethod
    def to_domain(orm: TestCaseORM) -> TestCase:
        return TestCase(
            id=orm.id,
            assignment_id=orm.assignment_id,
            input_data=orm.input_data,
            expected_output=orm.expected_output,
            check_type=orm.check_type,
        )

    @staticmethod
    def to_dict(domain: TestCase) -> dict[str, Any]:
        return {
            "id": domain.id,
            "assignment_id": domain.assignment_id,
            "input_data": domain.input_data,
            "expected_output": domain.expected_output,
            "check_type": domain.check_type,
        }
