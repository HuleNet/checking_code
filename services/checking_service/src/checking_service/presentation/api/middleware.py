from uuid import uuid4
from typing import Callable, Awaitable

from fastapi import Request, Response

from checking_service.infrastructure.core import set_request_id


async def logging_middleware(
    request: Request, call_next: Callable[[Request], Awaitable[Response]]
) -> Response:
    request_id = request.headers.get("X-Request-ID")

    if request_id is None:
        request_id = str(uuid4())

    set_request_id(request_id=request_id)

    try:
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response

    finally:
        set_request_id(None)
