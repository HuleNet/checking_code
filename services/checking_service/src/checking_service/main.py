from fastapi import FastAPI
from uvicorn import run

from checking_service.presentation.api import (
    main_router,
    register_exception_handlers,
)


app = FastAPI()
app.include_router(router=main_router)
register_exception_handlers(app=app)


if __name__ == "__main__":
    run(
        "checking_service.main:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
    )
