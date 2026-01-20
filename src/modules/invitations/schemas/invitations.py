from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from src.core.db.enums import InvitationStatus, TeamRole


class BasicResponse(BaseModel):
    success: bool
    message: str


class UserMini(BaseModel):
    id: UUID
    first_name: str
    last_name: str
    roles: list[TeamRole]


class ProjectInfo(BaseModel):
    id: UUID
    name: str = Field(..., max_length=100)
    description: str
    team_leader: UserMini
    participants: list[UserMini]


class InvitationInfoResponse(BaseModel):
    invitation_id: UUID
    notification_id: UUID
    status: InvitationStatus
    project: ProjectInfo


class AcceptedDeadlineResponse(BaseModel):
    invitation_id: UUID
    accepted_deadline: datetime
    is_expired: bool
