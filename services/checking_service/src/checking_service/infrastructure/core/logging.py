from sys import stdout
from logging import Formatter, Filter, LogRecord, StreamHandler, getLogger
from json import dumps
from datetime import datetime, timezone
from contextvars import ContextVar
from typing import Any


request_id_ctx: ContextVar[str | None] = ContextVar("request_id", default=None)


def set_request_id(request_id: str | None) -> None:
    request_id_ctx.set(request_id)


def get_request_id() -> str | None:
    return request_id_ctx.get()


class JsonFormatter(Formatter):
    def format(self, record: LogRecord) -> str:
        log: dict[str, Any] = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "service": "checking_service",
            "logger": record.name,
            "msg": record.getMessage(),
        }

        request_id = get_request_id()
        if request_id:
            log["request_id"] = request_id

        if hasattr(record, "extra"):
            log.update(record.extra)

        if record.exc_info:
            log["exc"] = self.formatException(record.exc_info)

        return dumps(log, ensure_ascii=False)


class ExtraFilter(Filter):
    def filter(self, record: LogRecord) -> bool:
        if not hasattr(record, "extra"):
            record.extra = {}

        return True


def setup_logging(level: str = "INFO") -> None:
    handler = StreamHandler(stdout)
    handler.setFormatter(JsonFormatter())
    handler.addFilter(ExtraFilter())
    root = getLogger()
    root.handlers.clear()
    root.setLevel(level)
    root.addHandler(handler)
