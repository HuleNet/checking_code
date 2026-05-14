from pathlib import Path

from shared.base_executor import BaseExecutor
from shared.models import CompileResult


class PythonExecutor(BaseExecutor):
    @property
    def source_filename(self) -> str:
        return "main.py"

    def compile(self, workdir: Path) -> CompileResult | None:
        return None

    def run_command(self, workdir: Path) -> list[str]:
        return ["python", "main.py"]


if __name__ == "__main__":
    executor = PythonExecutor()
    request = executor.load_request()
    response = executor.execute(request)
    executor.save_response(response)
