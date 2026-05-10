from enum import Enum


class BaseEnum(str, Enum):
    @classmethod
    def values(cls) -> list[str]:
        return [e.value for e in cls]
