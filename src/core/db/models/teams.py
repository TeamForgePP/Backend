from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Enum, DateTime, text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from uuid import uuid4
from enum import Enum as Enumm
from src.core.db.base import Base

class UserStatus(Enumm):
    Owner = "owner"
    Member = "member"
    Invited = "invited"

class Teams(Base):
    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    #project_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False)
    #user_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    status: Mapped[UserStatus] = mapped_column(Enum(UserStatus), nullable=False)
    updated_at: Mapped[DateTime] = mapped_column(DateTime, nullable=False, default=text("now()"))