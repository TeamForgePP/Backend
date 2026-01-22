from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from src.core.db.enums import ReportStatus, TeamRole, UserStatus


class BasicResponse(BaseModel):
    success: bool
    message: str


class AllowedActions(BaseModel):
    can_edit: bool
    can_finish: bool
    reports: bool


class ProjectTeamMember(BaseModel):
    id: UUID
    first_name: str
    last_name: str
    roles: list[TeamRole]
    status: UserStatus


class ReportEditInfo(BaseModel):
    editor_id: UUID | None = None
    editor_fn: str | None = None
    editor_ln: str | None = None
    updated_at: datetime | None = None


class ProjectReport(BaseModel):
    id: UUID
    file_key: str
    view_url: str
    status: ReportStatus
    content_type: str | None = None
    size_bytes: int | None = None
    creator_id: UUID | None = None
    creator_fn: str
    creator_ln: str
    title: str
    description: str | None = None
    teacher_note: str | None = None
    edit: ReportEditInfo | None = None


class ProjectDetailResponse(BaseModel):
    project_id: UUID
    project_name: str
    git: str | None = None
    description: str
    team: list[ProjectTeamMember]
    reports: list[ProjectReport]
    allowed_actions: AllowedActions


class PresignedPost(BaseModel):
    url: str
    fields: dict[str, str]
    method: str = "POST"


class ReportUploadInfo(BaseModel):
    id: UUID
    file_key: str
    status: ReportStatus
    view_url: str
    content_type: str | None = None
    size_bytes: int | None = None
    upload: PresignedPost | None = None


class CreateReportResponse(BaseModel):
    success: bool
    message: str
    report: ReportUploadInfo


class FinalizeReportResponse(BaseModel):
    success: bool
    message: str
    report: ReportUploadInfo


class EditReportResponse(BaseModel):
    success: bool
    message: str
    report: ProjectReport
