from fastapi import FastAPI

from task_service.presentation.api.routes import main_router


app = FastAPI()
app.include_router(router=main_router)
