from pathlib import Path
from subprocess import run

from shared.base_executor import BaseExecutor
from shared.models import CompileResult


CSPROJ = """
<Project Sdk="Microsoft.NET.Sdk">

  <PropertyGroup>
    <OutputType>Exe</OutputType>
    <TargetFramework>net8.0</TargetFramework>
    <ImplicitUsings>enable</ImplicitUsings>
    <Nullable>enable</Nullable>
  </PropertyGroup>

</Project>
"""


class CSharpExecutor(BaseExecutor):
    @property
    def source_filename(self) -> str:
        return "Program.cs"

    def compile(self, workdir: Path) -> CompileResult | None:
        csproj = workdir / "JudgeSolution.csproj"
        csproj.write_text(CSPROJ)
        process = run(
            ["dotnet", "build", "-c", "Release", "-o", "out"],
            cwd=workdir,
            capture_output=True,
            text=True,
        )
        return CompileResult(
            success=process.returncode == 0,
            stdout=process.stdout,
            stderr=process.stderr,
            exit_code=process.returncode,
        )

    def run_command(self, workdir: Path) -> list[str]:
        return [
            "dotnet",
            str(workdir / "out" / "JudgeSolution.dll"),
        ]

if __name__ == "__main__":
    executor = CSharpExecutor()
    request = executor.load_request()
    response = executor.execute(request)
    executor.save_response(response)
