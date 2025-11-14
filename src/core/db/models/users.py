from __future__ import annotations

from uuid import UUID, uuid4

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from ..base import Base
from ..enums import UserRole


class User(Base):
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)

    last_name: Mapped[str] = mapped_column(String(35), nullable=False)
    first_name: Mapped[str] = mapped_column(String(20), nullable=False)
    patronymic: Mapped[str | None] = mapped_column(String(35))

    email: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    password: Mapped[str] = mapped_column(String(50), nullable=False)

    user_type: Mapped[UserRole] = mapped_column(
        Enum(UserRole, name="users_role", create_constraint=True), nullable=False
    )

    avatar_url: Mapped[str | None] = mapped_column(Text)

    group_id: Mapped[UUID | None] = mapped_column(ForeignKey("groups.id", ondelete="SET NULL"))

    in_team: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="false")

    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )
