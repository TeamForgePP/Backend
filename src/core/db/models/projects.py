from uuid import UUID, uuid4

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from src.core.db.base import Base


class Projects(Base):
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)

    teamlead_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"), nullable=False
    )

    curator_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"), doc="преподаватель"
    )

    name: Mapped[str] = mapped_column(String(100), nullable=False)

    description: Mapped[str | None] = mapped_column(Text)

    is_completed: Mapped[bool] = mapped_column(Boolean, nullable=False, default="false")

    # avatar_url: Mapped[str | None] = mapped_column(Text) будущий функционал

    github_url: Mapped[str | None] = mapped_column(Text, default="")

    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=func.now()
    )

    updated_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=func.now(), onupdate=func.now()
    )
