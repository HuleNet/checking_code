from pathlib import Path
from json import dumps, loads
from typing import Any


def write_json(path: Path, data: Any) -> None:
    if hasattr(data, 'to_dict'):
        data = data.to_dict()
        
    elif hasattr(data, '__dataclass_fields__'):
        from dataclasses import asdict
        data = asdict(data)
        
    path.write_text(dumps(data, ensure_ascii=False), encoding="utf-8")


def read_json(path: Path) -> dict:
    return loads(path.read_text(encoding="utf-8"))
