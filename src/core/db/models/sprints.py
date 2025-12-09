from uuid import UUID, uuid4

from sqlalchemy import Date, DateTime, Enum, ForeignKey, SmallInteger, String, func
from sqlalchemy.orm import Mapped, mapped_column

from src.core.db.base import Base
from src.core.db.enums import SprintStatus


class Sprints(Base):
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)

    project_id: Mapped[UUID] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    seq: Mapped[int] = mapped_column(SmallInteger, nullable=False)

    name: Mapped[str] = mapped_column(String(100), nullable=False)

    description: Mapped[str | None] = mapped_column(String(500))

    goal: Mapped[str | None] = mapped_column(String(100))

    start: Mapped[Date] = mapped_column(Date, nullable=False)

    deadline: Mapped[Date] = mapped_column(Date, nullable=False)

    status: Mapped[SprintStatus] = mapped_column(
        Enum(SprintStatus, name="sprint_status", create_constraint=True),
        nullable=False,
        default=SprintStatus.UPCOMING,
    )

    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=func.now()
    )

    updated_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=func.now(), onupdate=func.now()
    )
