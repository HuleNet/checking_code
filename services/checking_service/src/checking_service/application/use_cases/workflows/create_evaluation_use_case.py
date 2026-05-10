from uuid import uuid4

from checking_service.domain.events.evaluation_events import EvaluationStartedEvent
from checking_service.domain.errors import DomainError
from checking_service.application.dto.evaluation import (
    CreateEvaluationDTO,
    EvaluationDTO,
)
from checking_service.application.dto.submission import SubmissionDTO
from checking_service.application.dto.mappers import (
    EvaluationMapper,
    ExecutionCaseMapper,
    DomainEnumsMapper,
)
from checking_service.application.use_cases.test_case import (
    GetTestCasesByAssignmentUseCase,
)
from checking_service.application.ports import UnitOfWork
from checking_service.application.errors import (
    ValidationError,
    NotFoundError,
    ApplicationError,
    InternalError,
)


class CreateEvaluationUseCase:
    def __init__(
        self,
        uow: UnitOfWork,
        get_test_cases: GetTestCasesByAssignmentUseCase,
    ) -> None:
        self.uow = uow
        self.get_test_cases = get_test_cases

    async def execute(
        self,
        dto: SubmissionDTO,
    ) -> EvaluationDTO:
        try:
            test_cases = await self.get_test_cases.execute(
                assignment_id=dto.assignment_id
            )

            if not test_cases:
                raise NotFoundError(
                    message="TestCases not found",
                    details={
                        "entity": "test_case",
                        "assignment_id": dto.assignment_id,
                    },
                )

            evaluation = EvaluationMapper.to_domain(
                dto=CreateEvaluationDTO(
                    submission_id=dto.id, tests_total=len(test_cases)
                ),
                id=uuid4(),
            )
            execution_cases = [
                ExecutionCaseMapper.to_domain(
                    id=uuid4(), evaluation_id=evaluation.id, test_case=test_case
                )
                for test_case in test_cases
            ]
            evaluation._add_event(
                event=EvaluationStartedEvent(
                    evaluation_id=evaluation.id,
                    code=dto.code,
                    language=DomainEnumsMapper.map_language(dto.language),
                )
            )

            async with self.uow as uow:
                result = await uow.evaluation_repo.add(evaluation=evaluation)
                await self.uow.execution_case_repo.add_many(
                    execution_cases=execution_cases
                )
                await uow.track(entity=result)
                await uow.commit()

            return EvaluationMapper.to_dto(domain=result)

        except DomainError as exc:
            raise ValidationError(
                message=exc.message,
                details=exc.details,
            ) from exc

        except ApplicationError:
            raise

        except Exception as exc:
            raise InternalError(
                message="Failed to create Evaluation",
                details={
                    "entity": "evaluation",
                    "submission_id": dto.id,
                    "assignment_id": dto.assignment_id,
                },
            ) from exc
