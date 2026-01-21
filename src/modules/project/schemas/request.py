from uuid import UUID

from pydantic import BaseModel


class FileMeta(BaseModel):
    content_type: str
    size_bytes: int


class CreateReportRequest(BaseModel):
    project_id: UUID
    title: str
    description: str | None = None
    teacher_note: str | None = None
    file: FileMeta


class FinalizeReportRequest(BaseModel):
    report_id: UUID


class EditReportRequest(BaseModel):
    report_id: UUID
    project_id: UUID | None = None
    title: str
    description: str | None = None
    teacher_note: str | None = None


class EditProjectRequest(BaseModel):
    project_id: UUID
    name: str | None = None
    github_url: str | None = None
    description: str | None = None
    invited: list[UUID] | None = None
    deleted: list[UUID] | None = None


class TeamExcludeRequest(BaseModel):
    project_id: UUID
    user_id: UUID


class FinishProjectRequest(BaseModel):
    project_id: UUID
