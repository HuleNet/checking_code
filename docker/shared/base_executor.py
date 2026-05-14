from abc import ABC, abstractmethod
from pathlib import Path
from subprocess import run, TimeoutExpired
from tempfile import TemporaryDirectory
from time import perf_counter

from shared.models import (
    CompileResult,
    RuntimeRequest,
    RuntimeResponse,
    TestCase,
    TestResult,
)
from shared.protocol import REQUEST_FILE, RESULT_FILE
from shared.utils import read_json, write_json


class BaseExecutor(ABC):
    def load_request(self) -> RuntimeRequest:
        data = read_json(REQUEST_FILE)
        return RuntimeRequest(
            code=data["code"],
            tests=[
                TestCase(
                    id=test["id"],
                    stdin=test["stdin"],
                )
                for test in data["tests"]
            ],
            time_limit_sec=data["time_limit_sec"],
        )

    def save_response(self, response: RuntimeResponse) -> None:
        write_json(RESULT_FILE, response)

    @property
    @abstractmethod
    def source_filename(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def compile(self, workdir: Path) -> CompileResult | None:
        raise NotImplementedError

    @abstractmethod
    def run_command(self, workdir: Path) -> list[str]:
        raise NotImplementedError

    def execute(self, request: RuntimeRequest) -> RuntimeResponse:
        with TemporaryDirectory() as tmp:
            workdir = Path(tmp)
            source_file = workdir / self.source_filename
            source_file.write_text(request.code)
            compile_result = self.compile(workdir)

            if compile_result and not compile_result.success:
                return RuntimeResponse(
                    compile_result=compile_result,
                    results=[],
                )

            results: list[TestResult] = []
            
            for test in request.tests:
                result = self.run_test(
                    workdir=workdir,
                    test=test,
                    time_limit_sec=request.time_limit_sec,
                )
                results.append(result)

            return RuntimeResponse(
                compile_result=compile_result,
                results=results,
            )

    def run_test(
        self,
        workdir: Path,
        test: TestCase,
        time_limit_sec: int,
    ) -> TestResult:
        started_at = perf_counter()

        try:
            completed = run(
                self.run_command(workdir),
                input=test.stdin,
                text=True,
                capture_output=True,
                cwd=workdir,
                timeout=time_limit_sec,
            )
            execution_time_ms = int(
                (perf_counter() - started_at) * 1000
            )
            return TestResult(
                id=test.id,
                stdout=completed.stdout,
                stderr=completed.stderr,
                exit_code=completed.returncode,
                execution_time_ms=execution_time_ms,
            )
            
        except TimeoutExpired as exc:
            execution_time_ms = int(
                (perf_counter() - started_at) * 1000
            )
            return TestResult(
                id=test.id,
                stdout=exc.stdout or "",
                stderr="Timeout",
                exit_code=-1,
                execution_time_ms=execution_time_ms,
            )
