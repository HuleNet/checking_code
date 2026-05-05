from sqlalchemy import inspect
from sqlalchemy.orm import DeclarativeBase

from task_service.infrastructure.core import get_settings_cached


MAX_CODE_LENGTH = get_settings_cached().max_code_length


class BaseModel(DeclarativeBase):
    def __repr__(self) -> str:
        state = inspect(self)
        fields = []

        for column in self.__mapper__.columns:
            key = column.key

            if key in state.unloaded:
                value = "<unloaded>"
            else:
                value = getattr(self, key)

            fields.append(f"{key}={value!r}")

        return f"{self.__class__.__name__}({', '.join(fields)})"
