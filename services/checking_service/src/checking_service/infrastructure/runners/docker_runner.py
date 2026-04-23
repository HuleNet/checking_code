from io import BytesIO
from dataclasses import dataclass
from json import dumps, loads
from tarfile import TarInfo, open as tarfile_open
from asyncio import to_thread
from time import time, sleep
from typing import Any
from pathlib import Path

from docker import from_env
from docker.models.containers import Container

from checking_service.domain.enums import Language
from checking_service.domain.entities import ExecutionCase
from checking_service.application.models.runner_result import RunnerResult
from checking_service.application.ports import Runner


@dataclass
class LanguageConfig:
    image: str
    filename: str
    compile: list[str] | None
    run: list[str]


LANG_CONFIG: dict[Language, LanguageConfig] = {
    Language.PYTHON: LanguageConfig(
        image="python:3.11-alpine",
        filename="main.py",
        compile=None,
        run=["python3", "main.py"],
    ),
    Language.CSHARP: LanguageConfig(
        image="mcr.microsoft.com/dotnet/sdk:7.0",
        filename="Program.cs",
        compile=["dotnet", "build", "-o", "out"],
        run=["dotnet", "out/Program.dll"],
    ),
}


class DockerRunner(Runner):
    def __init__(
        self,
        timeout_sec: int,
        memory_limit_mb: int,
        cpu_limit: float,
    ) -> None:
        self.client = from_env()
        self.timeout_sec = timeout_sec
        self.memory_limit_mb = memory_limit_mb
        self.cpu_limit = cpu_limit
        self.executor_path = Path(__file__).parent / "executor.py"

    async def run(
        self,
        code: str,
        language: Language,
        execution_cases: list[ExecutionCase],
    ) -> list[RunnerResult]:
        return await to_thread(self._run_sync, code, language, execution_cases)

    def _run_sync(
        self,
        code: str,
        language: Language,
        execution_cases: list[ExecutionCase],
    ) -> list[RunnerResult]:
        config = LANG_CONFIG[language]
        container: Container | None = None
        start_time = time()

        try:
            container = self.client.containers.create(
                image=config.image,
                command=["sh", "-c", "python3 executor.py"],
                working_dir="/tmp",
                mem_limit=f"{self.memory_limit_mb}m",
                cpu_period=100_000,
                cpu_quota=int(self.cpu_limit * 100_000),
                network_disabled=True,
                pids_limit=64,
                security_opt=["no-new-privileges"],
                read_only=False,
            )
            self._copy_files(container, code, execution_cases, config)
            container.start()
            timeout = False
            
            while True:
                container.reload()
                status = container.status

                if status in ("exited", "dead"):
                    break

                if time() - start_time > self.timeout_sec:
                    container.kill()
                    timeout = True
                    break

                sleep(0.05)

            container.reload()
            state = container.attrs.get("State", {})
            exit_code = state.get("ExitCode", -1)
            oom_killed = state.get("OOMKilled", False)
            stdout = container.logs(stdout=True, stderr=False).decode(errors="ignore")
            stderr = container.logs(stdout=False, stderr=True).decode(errors="ignore")
            duration_ms = int((time() - start_time) * 1000)

            if timeout:
                return self._fail_all(execution_cases, duration_ms, "TIMEOUT")

            if oom_killed:
                return [
                    RunnerResult(
                        execution_case_id=case.id,
                        stdout="",
                        stderr="MEMORY_LIMIT_EXCEEDED",
                        execution_time_ms=duration_ms,
                        exit_code=-1,
                        timeout=False,
                        memory_exceeded=True,
                    )
                    for case in execution_cases
                ]

            if exit_code != 0:
                return self._fail_all(
                    execution_cases,
                    duration_ms,
                    stderr or f"EXIT_CODE_{exit_code}",
                )

            try:
                data = loads(stdout)
                
            except Exception:
                return self._fail_all(
                    execution_cases,
                    duration_ms,
                    f"INVALID_JSON\nstdout:\n{stdout}\nstderr:\n{stderr}",
                )

            if isinstance(data, dict) and data.get("compile_error"):
                return self._compile_fail_all(
                    execution_cases,
                    data.get("stderr", ""),
                )

            result_map: dict[str, dict[str, Any]] = {
                r["id"]: r for r in data
            }

            return [
                RunnerResult(
                    execution_case_id=case.id,
                    stdout=result_map[str(case.id)]["stdout"],
                    stderr=result_map[str(case.id)]["stderr"],
                    execution_time_ms=result_map[str(case.id)]["execution_time_ms"],
                    exit_code=result_map[str(case.id)]["exit_code"],
                    timeout=result_map[str(case.id)]["timeout"],
                    memory_exceeded=False,
                )
                for case in execution_cases
            ]

        except Exception as e:
            duration_ms = int((time() - start_time) * 1000)
            return self._fail_all(execution_cases, duration_ms, f"RUNNER_ERROR: {str(e)}")

        finally:
            if container:
                try:
                    container.remove(force=True)
                    
                except Exception:
                    pass

    def _copy_files(
        self,
        container: Container,
        code: str,
        execution_cases: list[ExecutionCase],
        config: LanguageConfig,
    ) -> None:
        tar_stream = BytesIO()
        payload = {
            "code": code,
            "timeout": self.timeout_sec,
            "config": {
                "filename": config.filename,
                "compile": config.compile,
                "run": config.run,
            },
            "tests": [
                {"id": str(case.id), "input": case.input_data}
                for case in execution_cases
            ],
        }

        with tarfile_open(fileobj=tar_stream, mode="w") as tar:
            with open(self.executor_path, "rb") as f:
                data = f.read()

            ti = TarInfo(name="executor.py")
            ti.size = len(data)
            ti.mode = 0o755
            tar.addfile(ti, BytesIO(data))
            payload_bytes = dumps(payload).encode()
            ti = TarInfo(name="input.json")
            ti.size = len(payload_bytes)
            tar.addfile(ti, BytesIO(payload_bytes))

        tar_stream.seek(0)
        container.put_archive("/tmp", tar_stream.read())

    def _fail_all(self, execution_cases, duration_ms, error):
        return [
            RunnerResult(
                execution_case_id=case.id,
                stdout="",
                stderr=error,
                execution_time_ms=duration_ms,
                exit_code=-1,
                timeout=(error == "TIMEOUT"),
                memory_exceeded=False,
            )
            for case in execution_cases
        ]

    def _compile_fail_all(self, execution_cases, stderr):
        return [
            RunnerResult(
                execution_case_id=case.id,
                stdout="",
                stderr=stderr,
                execution_time_ms=0,
                exit_code=-1,
                timeout=False,
                memory_exceeded=False,
            )
            for case in execution_cases
        ]