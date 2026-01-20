from datetime import date
from uuid import UUID

from pydantic import BaseModel, Field

from src.core.db import TaskPriority, TaskStatus, TeamRole


class Project(BaseModel):
    id: UUID
    name: str


class SelectedSprint(BaseModel):
    id: UUID
    seq: int


class Performer(BaseModel):
    id: UUID
    first_name: str
    last_name: str
    avatar_url: str


class Task(BaseModel):
    id: UUID
    title: str
    tag: TeamRole | None = None
    status: TaskStatus
    deadline: date
    priority: TaskPriority
    performers: list[Performer] = Field(default_factory=list)
    key: str


class KanbanResponse(BaseModel):
    project: Project
    selected_sprint: SelectedSprint
    tasks: list[Task] = Field(default_factory=list)


class PerformerNewTask(BaseModel):
    id: UUID


class NewTaskRequest(BaseModel):
    sprint_id: UUID | None = None
    title: str
    description: str
    performers: list[PerformerNewTask] = Field(default_factory=list)
    priority: TaskPriority
    deadline: date
    tag: TeamRole | None = None


class MembersResponse(BaseModel):
    members: list[Performer] = Field(default_factory=list)


class TaskResponse(BaseModel):
    id: UUID
    title: str
    description: str
    performers: list[Performer] = Field(default_factory=list)
    priority: TaskPriority
    deadline: date
    tag: TeamRole | None = None
    key: str


class UpdateStatusRequest(BaseModel):
    task_id: UUID
    status: TaskStatus


class BasicResponse(BaseModel):
    success: bool
    message: str


class SprintItem(BaseModel):
    id: UUID
    label: str


class SprintsResponse(BaseModel):
    number: int
    sprints: list[SprintItem] = Field(default_factory=list)
