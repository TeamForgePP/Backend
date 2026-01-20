from uuid import UUID, uuid4

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from src.core.db.base import Base
from src.core.db.enums import UserRole


class Users(Base):
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)

    last_name: Mapped[str] = mapped_column(String(35), nullable=False)

    first_name: Mapped[str] = mapped_column(String(20), nullable=False)

    patronymic: Mapped[str | None] = mapped_column(String(35))

    email: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)

    password: Mapped[str] = mapped_column(String, nullable=False)

    user_type: Mapped[UserRole] = mapped_column(
        Enum(UserRole, name="users_role", create_constraint=True),
        nullable=False,
        default=UserRole.STUDENT,
    )

    avatar_url: Mapped[str | None] = mapped_column(Text)

    group_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("groups.id", ondelete="SET NULL"),
        index=True,
        nullable=True,
    )

    in_team: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=func.now()
    )

    updated_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=func.now(), onupdate=func.now()
    )
