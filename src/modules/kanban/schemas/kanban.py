from datetime import date
from uuid import UUID

from pydantic import BaseModel

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
    tags: list[TeamRole]
    status: TaskStatus
    deadline: date
    priority: TaskPriority
    performes: list[Performer]
    key: str


class KanbanResponse(BaseModel):
    project: Project
    selected_sprint: SelectedSprint
    tasks: list[Task]


class PerformerNewTask(BaseModel):
    id: UUID


class NewTaskRequest(BaseModel):
    sprint_id: UUID
    title: str
    description: str
    performes: list[PerformerNewTask]
    priority: TaskPriority
    deadline: date


class MembersResponse(BaseModel):
    members: list[Performer]


class TaskResponse(BaseModel):
    id: UUID
    title: str
    description: str
    users: list[
        Performer
    ]  # тут чуть по другому, чем в документации, тк таска может быть назначена нескольким типам
    priority: TaskPriority
    deadline: date


class UpdateStatusRequest(BaseModel):
    task_id: UUID
    status: TaskStatus


class BasicResponse(BaseModel):
    success: bool
    message: str
