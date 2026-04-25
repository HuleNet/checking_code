from fastapi import FastAPI

from checking_service.presentation.api import main_router, register_exception_handlers


app = FastAPI()
app.include_router(router=main_router)
register_exception_handlers(app=app)
