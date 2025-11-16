from uuid import UUID, uuid4

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from src.core.db import Base, NotificationType


class Notifications(Base):
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)

    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), nullable=False)

    type: Mapped[NotificationType] = mapped_column(
        Enum(NotificationType, name="notification_type", create_constraint=True), nullable=False
    )

    title: Mapped[str] = mapped_column(Text)

    message: Mapped[str] = mapped_column(Text)

    project_id: Mapped[UUID] = mapped_column(ForeignKey("projects.id"), nullable=False)

    is_read: Mapped[bool] = mapped_column(Boolean, default=False)

    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=func.now()
    )

    updated_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=func.now(), onupdate=func.now()
    )
