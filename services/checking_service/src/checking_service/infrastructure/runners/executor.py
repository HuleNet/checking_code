from json import load, dumps
from subprocess import run, TimeoutExpired
from time import time
from typing import Any


def run_process(cmd: list[str], input_data: str, timeout: int) -> dict[str, Any]:
    try:
        start = time()
        proc = run(
            cmd,
            input=input_data.encode(),
            capture_output=True,
            timeout=timeout,
        )
        return {
            "stdout": proc.stdout.decode(errors="ignore"),
            "stderr": proc.stderr.decode(errors="ignore"),
            "exit_code": proc.returncode,
            "timeout": False,
            "execution_time_ms": int((time() - start) * 1000),
        }

    except TimeoutExpired:
        return {
            "stdout": "",
            "stderr": "TIMEOUT",
            "exit_code": -1,
            "timeout": True,
            "execution_time_ms": int(timeout * 1000),
        }

    except Exception as e:
        return {
            "stdout": "",
            "stderr": f"RUNTIME_ERROR: {str(e)}",
            "exit_code": -1,
            "timeout": False,
            "execution_time_ms": 0,
        }


def main() -> None:
    try:
        with open("input.json", "r") as f:
            payload = load(f)
            
    except Exception as e:
        print(dumps({"fatal_error": f"invalid_input: {str(e)}"}))
        return

    code = payload["code"]
    tests = payload["tests"]
    timeout = payload["timeout"]
    config = payload["config"]
    filename = config["filename"]
    compile_cmd = config.get("compile")
    run_cmd = config["run"]

    try:
        with open(filename, "w") as f:
            f.write(code)
            
    except Exception as e:
        print(dumps({"fatal_error": f"write_failed: {str(e)}"}))
        return

    if compile_cmd:
        comp = run_process(compile_cmd, "", timeout)
        if comp["timeout"] or comp["exit_code"] != 0:
            print(dumps({
                "compile_error": True,
                "stderr": comp["stderr"],
            }))
            return

    results: list[dict[str, Any]] = []

    for test in tests:
        result = run_process(run_cmd, test["input"], timeout)
        results.append({
            "id": test["id"],
            "stdout": result["stdout"],
            "stderr": result["stderr"],
            "exit_code": result["exit_code"],
            "timeout": result["timeout"],
            "execution_time_ms": result["execution_time_ms"],
        })

    print(dumps(results))


if __name__ == "__main__":
    main()