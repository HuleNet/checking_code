from dataclasses import dataclass
from hashlib import sha256


@dataclass(frozen=True)
class CodeHash:
    value: str

    @staticmethod
    def from_code(code: str) -> "CodeHash":
        normalized = code.strip()
        return CodeHash(value=sha256(normalized.encode()).hexdigest())
