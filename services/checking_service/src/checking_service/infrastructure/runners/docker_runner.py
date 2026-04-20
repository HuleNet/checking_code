from os import path
from tempfile import TemporaryDirectory
from asyncio import gather, create_subprocess_exec, subprocess, wait_for, TimeoutError
from time import monotonic

from checking_service.domain.enums import Language
from checking_service.domain.entities import ExecutionCase
from checking_service.application.models.runner_result import RunnerResult
from checking_service.application.ports import Runner


class DockerRunner(Runner):
    def __init__(
        self, timeout_sec: int, memory_limit_mb: int, cpu_limit: float
    ) -> None:
        self.timeout_sec = timeout_sec
        self.memory_limit_mb = memory_limit_mb
        self.cpu_limit = cpu_limit
        self.language_map = {
            Language.PYTHON: ("python:3.13-slim", "main.py", "python main.py"),
        }

    async def run(
        self, code: str, language: Language, execution_cases: list[ExecutionCase]
    ) -> list[RunnerResult]:
        tasks = [
            self._run_one(code=code, language=language, execution_case=execution_case)
            for execution_case in execution_cases
        ]
        return await gather(*tasks)

    async def _run_one(
        self, code: str, language: Language, execution_case: ExecutionCase
    ) -> RunnerResult:
        image, filename, command = self._get_language_specs(language=language)

        with TemporaryDirectory() as tmpdir:
            file_path = path.join(tmpdir, filename)

            with open(file_path, "w") as f:
                f.write(code)

            container_name = f"runner-{execution_case.id}"
            docker_cmd = [
                "docker",
                "run",
                "--rm",
                "--name",
                container_name,
                "--network",
                "none",
                "--read-only",
                "--pids-limit",
                "64",
                "--memory",
                f"{self.memory_limit_mb}m",
                "--cpus",
                str(self.cpu_limit),
                "-v",
                f"{tmpdir}:/app:ro",
                "-w",
                "/app",
                image,
                "sh",
                "-c",
                command,
            ]
            start = monotonic()

            try:
                proc = await create_subprocess_exec(
                    *docker_cmd,
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                )

                try:
                    stdout, stderr = await wait_for(
                        proc.communicate(input=execution_case.input_data.encode()),
                        timeout=self.timeout_sec,
                    )
                    timeout = False

                except TimeoutError:
                    timeout = True
                    await self._kill_container(name=container_name)
                    stdout, stderr = b"", b"Time limit exceeded"

                end = monotonic()
                exit_code = proc.returncode if proc.returncode is not None else 1
                memory_limit_exceeded = exit_code == 137 and not timeout

                return RunnerResult(
                    execution_case_id=execution_case.id,
                    stdout=stdout.decode(errors="replace"),
                    stderr=stderr.decode(errors="replace"),
                    execution_time_ms=int((end - start) * 1000),
                    exit_code=proc.returncode if proc.returncode is not None else 1,
                    timeout=timeout,
                    memory_exceeded=memory_limit_exceeded,
                )

            except Exception as exc:
                return RunnerResult(
                    execution_case_id=execution_case.id,
                    stdout="",
                    stderr=str(exc),
                    execution_time_ms=0,
                    exit_code=1,
                    timeout=False,
                    memory_exceeded=False,
                )

    def _get_language_specs(self, language: Language) -> tuple[str, str, str]:
        if language not in self.language_map:
            raise ValueError(f"Unsupported language:{language}")

        return self.language_map[language]

    async def _kill_container(self, name: str) -> None:
        try:
            proc = await create_subprocess_exec(
                "docker",
                "kill",
                name,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            await proc.communicate()

        except Exception:
            pass
