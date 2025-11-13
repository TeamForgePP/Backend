from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Enum, ForeignKey, String, Boolean, DateTime, text, Text
from sqlalchemy.dialects.postgresql import UUID
from enum import Enum as Enumm
from uuid import uuid4
from src.core.db.base import Base

class NotificationType(Enumm):
    NewTask = "new_task"
    NewInvite = "new_invite"
    ProjectClosed = "project_closed"
    Deadline = "deadline"
    RemoverFromProject = "removed_from_project"

class Notifications(Base):
    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    #user_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    type: Mapped[NotificationType] = mapped_column(Enum(NotificationType))
    title: Mapped[str] = mapped_column(Text)
    message: Mapped[str] = mapped_column(Text)
    #project_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False)
    is_read: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[DateTime] = mapped_column(DateTime, nullable=False, default=text("now()"))