from typing import Literal


EvaluationStatus = Literal[
    "PENDING",
    "RUNNING",
    "PASSED",
    "FAILED",
    "MEMORY_EXCEEDED",
    "SYSTEM_ERROR",
]
