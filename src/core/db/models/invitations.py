from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Enum, ForeignKey, DateTime, text
from sqlalchemy.dialects.postgresql import UUID
from enum import Enum as Enumm
from uuid import uuid4
from src.core.db.base import Base

class InvitationStatus(Enumm):
    Posted = "posted"
    Rejected = "rejected"
    Accepted = "accepted"

class Invitations(Base):
    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    #notification_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("notifications.id"), nullable=False)
    #project_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False)
    #invited_user_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    #invited_by_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    status: Mapped[InvitationStatus] = mapped_column(Enum(InvitationStatus), default=text("PENDING"))
    created_at: Mapped[DateTime] = mapped_column(DateTime, nullable=False, default=text("now()"))