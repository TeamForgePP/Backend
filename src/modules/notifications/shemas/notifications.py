from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from src.core.db import InvitationStatus, NotificationType, TeamRole


class Notification(BaseModel):
    id: UUID
    type: NotificationType
    title: str
    message: str
    is_read: bool
    created_at: datetime
    invitation_id: UUID | None


class NotificationsResponse(BaseModel):
    notifications: list[Notification]
    unread_count: int


class TeamLeader(BaseModel):
    id: UUID
    first_name: str
    last_name: str
    roles: list[TeamRole]


class Participant(BaseModel):
    id: UUID
    first_name: str
    last_name: str
    roles: list[TeamRole]


class Project(BaseModel):
    id: UUID
    name: str = Field(..., max_length=100)
    description: str
    team_leader: TeamLeader
    participants: list[Participant]


class InvitationResponse(BaseModel):
    invitation_id: UUID
    notification_id: UUID
    status: InvitationStatus
    project: Project


class BasicResponse(BaseModel):
    success: bool
    message: str
