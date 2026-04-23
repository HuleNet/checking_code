from fastapi import FastAPI

from checking_service.presentation.api import main_router


app = FastAPI()
app.include_router(router=main_router)
