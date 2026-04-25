from asyncio import sleep
from random import uniform
from functools import wraps
from typing import Callable


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

                # exc для logger
                except exceptions as exc:
                    if attempt == attempts:
                        raise

                    delay = min(max_delay, base_delay * (2 ** (attempt - 1)))
                    delay += uniform(0, delay * 0.2)

                    await sleep(delay)

        return wrapper

    return decorator
