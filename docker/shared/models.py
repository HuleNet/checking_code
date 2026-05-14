from dataclasses import dataclass, asdict
from typing import Optional, Any


@dataclass(slots=True)
class TestCase:
    id: str
    stdin: str


@dataclass(slots=True)
class RuntimeRequest:
    code: str
    tests: list[TestCase]
    time_limit_sec: int


@dataclass(slots=True)
class CompileResult:
    success: bool
    stdout: str
    stderr: str
    exit_code: int


@dataclass(slots=True)
class TestResult:
    id: str
    stdout: str
    stderr: str
    exit_code: int
    execution_time_ms: int


@dataclass(slots=True)
class RuntimeResponse:
    compile_result: Optional[CompileResult]
    results: list[TestResult]

    def to_dict(self) -> dict:
        def _convert(obj: Any) -> Any:
            
            if isinstance(obj, list):
                return [_convert(item) for item in obj]
            
            elif hasattr(obj, '__dataclass_fields__'):
                return {k: _convert(v) for k, v in asdict(obj).items()}
            
            return obj
        
        return _convert(self)
