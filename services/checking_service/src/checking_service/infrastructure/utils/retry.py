from logging import getLogger
from asyncio import sleep
from random import uniform
from functools import wraps
from typing import Callable


logger = getLogger(__name__)


def retryable(
    *,
    attempts: int,
    base_delay: float,
    max_delay: float,
    exceptions: tuple[type[Exception], ...],
):
    def decorator(fn: Callable):
        @wraps(fn)
        async def wrapper(*args, **kwargs):
            for attempt in range(1, attempts + 1):
                try:
                    return await fn(*args, **kwargs)

                except exceptions as exc:
                    if attempt == attempts:
                        logger.error(
                            "retry_exhausted",
                            extra={
                                "extra": {
                                    "function": fn.__name__,
                                    "attempts": attempts,
                                }
                            },
                        )
                        raise

                    logger.warning(
                        "retryable_error",
                        extra={
                            "extra": {
                                "function": fn.__name__,
                                "attempt": attempt,
                                "attempts": attempts,
                                "error": repr(exc),
                            }
                        },
                    )
                    delay = min(max_delay, base_delay * (2 ** (attempt - 1)))
                    delay += uniform(0, delay * 0.2)

                    await sleep(delay)

        return wrapper

    return decorator
