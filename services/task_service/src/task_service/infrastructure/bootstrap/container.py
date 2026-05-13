from functools import cached_property

from task_service.domain.services import ScoringService
from task_service.infrastructure.db import SQLAlchemyUnitOfWork, SessionLocal
from task_service.infrastructure.checking_service import HTTPCheckingService
from task_service.infrastructure.core import get_settings_cached
from task_service.infrastructure.bootstrap.use_cases import UseCases


class Container:
    @cached_property
    def settings(self):
        return get_settings_cached()

    @cached_property
    def scoring_service(self) -> ScoringService:
        return ScoringService(
            max_attempts=self.settings.max_attempts,
            penalty_cap=self.settings.penalty_cap,
        )

    def uow(self) -> SQLAlchemyUnitOfWork:
        return SQLAlchemyUnitOfWork(session_factory=SessionLocal)

    @cached_property
    def checking_service(self) -> HTTPCheckingService:
        return HTTPCheckingService(base_url=self.settings.checking_service_url)

    @cached_property
    def use_cases(self) -> UseCases:
        return UseCases(
            uow_factory=self.uow,
            scoring_service=self.scoring_service,
            checking_service=self.checking_service,
            settings=self.settings,
        )


container = Container()
