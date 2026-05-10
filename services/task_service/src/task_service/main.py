from fastapi import FastAPI
from uvicorn import run

from task_service.presentation.api.routes import main_router


app = FastAPI()
app.include_router(router=main_router)


if __name__ == "__main__":
    run(
        "task_service.main:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
    )
