from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder

from checking_service.application.errors import (
    ApplicationError,
    ValidationError,
    NotFoundError,
    InternalError,
)


def _resolve_status_code(exc: ApplicationError) -> int:
    if isinstance(exc, ValidationError):
        return 400

    if isinstance(exc, NotFoundError):
        return 404

    if isinstance(exc, InternalError):
        return 500

    return 500


def _build_error_response(exc: ApplicationError) -> dict:
    return {
        "error": {
            "code": exc.code,
            "message": exc.message,
            "details": exc.details or {},
        }
    }


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(ApplicationError)
    async def application_exception_handler(
        request: Request, exc: ApplicationError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=_resolve_status_code(exc=exc),
            content=jsonable_encoder(_build_error_response(exc)),
        )

    @app.exception_handler(Exception)
    async def unexpected_exception_handler(
        request: Request,
        exc: Exception,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=500,
            content={
                "error": {
                    "code": "unexpected_error",
                    "message": "Unexpected internal server error",
                    "details": {},
                }
            },
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request,
        exc: RequestValidationError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=422,
            content={
                "error": {
                    "code": "validation_error",
                    "message": "Request validation failed",
                    "details": exc.errors(),
                }
            },
        )
