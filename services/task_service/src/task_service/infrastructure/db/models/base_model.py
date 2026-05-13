from sqlalchemy import inspect
from sqlalchemy.orm import DeclarativeBase


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
