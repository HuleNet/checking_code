from fastapi import FastAPI

from checking_service.infrastructure.core import get_settings_cached

settings = get_settings_cached()


app = FastAPI()


@app.get(path="/")
def health_check() -> str:
    return f"{settings.db_name}"
