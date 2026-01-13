from datetime import date
from uuid import UUID

from pydantic import BaseModel


class CurrentSprint(BaseModel):
    id: UUID
    seq: int
    name: str
    goal: str
    description: str
    estimated_deadline: date


class FutureCompletedSprint(BaseModel):
    id: UUID
    seq: int
    name: str


class AllSprintsResponse(BaseModel):
    current_sprint: CurrentSprint | None = None
    future_sprints: list[FutureCompletedSprint]
    completed_sprints: list[FutureCompletedSprint]


class Sprint(BaseModel):
    name: str
    start_date: date
    end_date: date
    goal: str
    description: str


class BasicResponse(BaseModel):
    success: bool
    message: str
