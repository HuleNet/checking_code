from typing import Any

from checking_service.domain.entities import ExecutionCase
from checking_service.infrastructure.db.models import ExecutionCaseORM


class ExecutionCaseMapper:
    @staticmethod
    def to_domain(orm: ExecutionCaseORM) -> ExecutionCase:
        return ExecutionCase(
            id=orm.id,
            evaluation_id=orm.evaluation_id,
            input_data=orm.input_data,
            expected_output=orm.expected_output,
            check_type=orm.check_type,
            stdout=orm.stdout,
            stderr=orm.stderr,
            execution_time_ms=orm.execution_time_ms,
            exit_code=orm.exit_code,
            is_timeout=orm.is_timeout,
            is_memory_exceeded=orm.is_memory_exceeded,
        )

    @staticmethod
    def to_dict(domain: ExecutionCase) -> dict[str, Any]:
        return {
            "id": domain.id,
            "evaluation_id": domain.evaluation_id,
            "input_data": domain.input_data,
            "expected_output": domain.expected_output,
            "check_type": domain.check_type,
            "stdout": domain.stdout,
            "stderr": domain.stderr,
            "execution_time_ms": domain.execution_time_ms,
            "exit_code": domain.exit_code,
            "is_timeout": domain.is_timeout,
            "is_memory_exceeded": domain.is_memory_exceeded,
        }
