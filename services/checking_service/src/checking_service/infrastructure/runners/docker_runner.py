from io import BytesIO
from json import dumps, loads
from tarfile import open as tar_open, TarInfo
from asyncio import get_running_loop
from pathlib import Path
from uuid import UUID

from docker import from_env
from docker.errors import APIError
from docker.models.containers import Container

from checking_service.application.dto.execution_case import ExecutionCaseResultDTO
from checking_service.application.ports import Runner
from checking_service.domain.entities import ExecutionCase
from checking_service.domain.value_objects import Language
from checking_service.application.errors import (
    RunnerExecutionError,
    RunnerMemoryError,
)


class DockerRunner(Runner):
    IMAGE_MAP = {
        Language.PYTHON: "judge-python:latest",
        Language.CSHARP: "judge-csharp:latest",
    }
    EXECUTOR_MAP = {
        Language.PYTHON: ["python3", "/runtime/python/executor.py"],
        Language.CSHARP: ["python3", "/runtime/csharp/executor.py"],
    }
    WORKSPACE_DIR = Path("/workspace")
    REQUEST_FILE = WORKSPACE_DIR / "request.json"
    RESULT_FILE = WORKSPACE_DIR / "result.json"

    def __init__(self, timeout_sec: int, memory_limit_mb: int, cpu_limit: float):
        self._client = from_env()
        self.timeout_sec = timeout_sec
        self.memory_limit_mb = memory_limit_mb
        self.cpu_limit = cpu_limit

    async def run(
        self, code: str, language: Language, execution_cases: list[ExecutionCase]
    ) -> list[ExecutionCaseResultDTO]:
        loop = get_running_loop()
        result = await loop.run_in_executor(
                None, self._run_sync, code, language, execution_cases
            )
        return result


    def _run_sync(
        self, code: str, language: Language, execution_cases: list[ExecutionCase]
    ):
        container: Container | None = None

        try:
            container = self._client.containers.create(
                image=self.IMAGE_MAP[language],
                network_disabled=True,
                mem_limit=f"{self.memory_limit_mb}m",
                nano_cpus=int(self.cpu_limit * 1_000_000_000),
                pids_limit=64,
            )
            container.start()
            request_payload = {
                "code": code,
                "tests": [
                    {"id": str(case.id), "stdin": case.input_data}
                    for case in execution_cases
                ],
                "time_limit_sec": self.timeout_sec,
            }
            request_json = dumps(request_payload, ensure_ascii=False)
            tar_stream = self._make_tar_archive(
                self.REQUEST_FILE.name, request_json.encode("utf-8")
            )
            container.put_archive(str(self.WORKSPACE_DIR), tar_stream)
            result = container.exec_run(self.EXECUTOR_MAP[language])

            if hasattr(result.output, "decode"):
                output_bytes = result.output

            else:
                output_bytes = b"".join(result.output)

            if result.exit_code != 0:              
                raise RunnerExecutionError(
                    message="Executor failed",
                    details={
                        "exit_code": result.exit_code,
                        "output": output_bytes.decode("utf-8"),
                    },
                )

            container.reload()

            if container.attrs["State"]["OOMKilled"]:
                raise RunnerMemoryError(
                    message="Container OOM killed",
                    details={"memory_limit_mb": self.memory_limit_mb},
                )

            tar_gen, _ = container.get_archive(str(self.RESULT_FILE))
            tar_bytes = b"".join(tar_gen)
            result_bytes = self._extract_file_from_tar(tar_bytes, self.RESULT_FILE.name)

            if not result_bytes:
                raise RunnerExecutionError(
                    message="result.json not found or empty",
                )

            response = loads(result_bytes.decode("utf-8"))
            return [
                ExecutionCaseResultDTO(
                    id=UUID(item["id"]),
                    stdout=item["stdout"],
                    stderr=item["stderr"],
                    exit_code=item["exit_code"],
                    execution_time_ms=item["execution_time_ms"],
                )
                for item in response["results"]
            ]

        except APIError as exc:
            raise RunnerExecutionError(
                message="Docker API error", details={"error": str(exc)}
            ) from exc

        finally:
            if container is not None:
                container.remove(force=True)

    def _make_tar_archive(self, filename: str, data: bytes) -> bytes:
        buf = BytesIO()

        with tar_open(fileobj=buf, mode="w") as tar:
            info = TarInfo(name=filename)
            info.size = len(data)
            tar.addfile(info, BytesIO(data))

        buf.seek(0)
        return buf.read()

    def _extract_file_from_tar(self, tar_bytes: bytes, filename: str) -> bytes | None:
        buf = BytesIO(tar_bytes)

        try:
            with tar_open(fileobj=buf) as tar:
                member = tar.getmember(filename)
                f = tar.extractfile(member)

                if f:
                    return f.read()

        except Exception:
            pass

        return None
