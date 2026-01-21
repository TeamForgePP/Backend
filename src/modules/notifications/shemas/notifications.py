from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from src.core.db import NotificationType


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


class BasicResponse(BaseModel):
    success: bool
    message: str
