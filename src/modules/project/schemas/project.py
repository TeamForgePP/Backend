from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from src.core.db.enums import TeamRole


class ProjectTeamMember(BaseModel):
    user_id: UUID
    first_name: str
    last_name: str
    group: str | None = None
    roles: list[TeamRole]


class ReportEditInfo(BaseModel):
    editor_id: UUID | None = None
    editor_fn: str | None = None
    editor_ln: str | None = None
    updated_at: datetime | None = None


class ProjectReport(BaseModel):
    id: UUID
    title: str
    description: str
    teacher_note: str
    edit: ReportEditInfo | None = None


class AllowedActions(BaseModel):
    can_edit: bool
    can_upload_file: bool
    can_delete: bool


class ProjectDetailResponse(BaseModel):
    project_id: UUID
    project_name: str
    team: list[ProjectTeamMember]
    git: str | None = None
    description: str
    reports: list[ProjectReport]
    allowed_actions: AllowedActions


class FileMeta(BaseModel):
    content_type: str | None = None
    size_bytes: int


class CreateReportRequest(BaseModel):
    project_id: UUID
    title: str
    description: str | None = None
    teacher_note: str | None = None
    file: FileMeta


class PresignedUpload(BaseModel):
    method: str
    url: str
    fields: dict[str, str]


class CreateReportResponse(BaseModel):
    report_id: UUID
    file_id: UUID
    upload: PresignedUpload


class ReportFileConfirmRequest(BaseModel):
    report_id: UUID
    file_id: UUID


class ReportFileConfirmResponse(BaseModel):
    status: str
    view_url: str
    content_type: str | None = None
    size_bytes: int
    upload: PresignedUpload | None = None


class EditReportRequest(BaseModel):
    report_id: UUID
    project_id: UUID
    title: str
    description: str | None = None
    teacher_note: str | None = None


class EditReportResponse(BaseModel):
    id: UUID
    title: str
    description: str
    teacher_note: str
    edit: ReportEditInfo | None = None
