from datetime import date
from uuid import UUID

from pydantic import BaseModel, Field

from src.core.db.enums import TeamRole


class SprintMap(BaseModel):
    id: UUID
    name: str = Field(max_length=100)
    seq: int
    deadline: date


class AllowedActions(BaseModel):
    can_delete: bool
    can_leave: bool


class Project(BaseModel):
    id: UUID
    name: str = Field(..., max_length=100)
    is_completed: bool = Field(default=False)
    current_sprint_name: str = Field(max_length=100)
    current_sprint_seq: int
    role: list[TeamRole]
    nearest_deadline: date | None
    sprint_map: list[SprintMap]
    allowed_actions: AllowedActions


class ProjectsResponse(BaseModel):
    projects: list[Project]


class BasicResponse(BaseModel):
    success: bool
    message: str


class TeamMember(BaseModel):
    id: UUID
    roles: list[TeamRole]


class CreateProjectRequest(BaseModel):
    name: str
    description: str | None = None
    team: list[TeamMember]
    git_organization: str = Field(default="")
