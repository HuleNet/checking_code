from fastapi import FastAPI

from checking_service.infrastructure.core import setup_logging
from checking_service.presentation.api import (
    main_router,
    register_exception_handlers,
    logging_middleware,
)


setup_logging()
app = FastAPI()
app.middleware("http")(logging_middleware)
app.include_router(router=main_router)
register_exception_handlers(app=app)
