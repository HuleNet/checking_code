from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class SubmissionDTO:
    id: UUID
    assignment_id: UUID
    language: str
    code: str


@dataclass(frozen=True)
class PreviewSubmissionDTO:
    assignment_id: UUID
    language: str
    code: str
