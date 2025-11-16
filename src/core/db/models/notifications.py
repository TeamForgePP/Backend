from uuid import UUID as pyUUID
from uuid import uuid4

from sqlalchemy import Boolean, DateTime, Enum, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from ..base import Base
from .enum import NotificationType


class Notifications(Base):
    id: Mapped[pyUUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)

    # user_id: Mapped[pyUUID] = mapped_column(
    #   UUID(as_uuid=True),
    #   ForeignKey("users.id"),
    #   nullable=False)

    type: Mapped[NotificationType] = mapped_column(Enum(NotificationType))

    title: Mapped[str] = mapped_column(Text)

    message: Mapped[str] = mapped_column(Text)

    # project_id: Mapped[pyUUID] = mapped_column(
    #   UUID(as_uuid=True),
    #   ForeignKey("projects.id"),
    #   nullable=False)

    is_read: Mapped[bool] = mapped_column(Boolean, default=False)

    created_at: Mapped[DateTime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )
