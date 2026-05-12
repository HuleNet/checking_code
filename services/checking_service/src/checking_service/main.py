from contextlib import asynccontextmanager

from fastapi import FastAPI
from uvicorn import run

from checking_service.infrastructure.broker import broker
from checking_service.presentation.api import (
    main_router,
    register_exception_handlers,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await broker.startup()
    yield
    await broker.shutdown()


app = FastAPI(lifespan=lifespan)
app.include_router(router=main_router)
register_exception_handlers(app=app)


if __name__ == "__main__":
    run(
        "checking_service.main:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
    )
