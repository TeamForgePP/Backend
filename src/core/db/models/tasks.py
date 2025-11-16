from uuid import UUID, uuid4

from sqlalchemy import DateTime, Enum, ForeignKey, SmallInteger, String, func
from sqlalchemy.orm import Mapped, mapped_column

from src.core.db.base import Base
from src.core.db.enums import TaskPriority, TaskStatus, TeamRole


class Tasks(Base):
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)

    project_id: Mapped[UUID] = mapped_column(ForeignKey("projects.id"), nullable=False)

    sprint_id: Mapped[UUID] = mapped_column(ForeignKey("sprints.id"), nullable=False)

    title: Mapped[str] = mapped_column(String(50), nullable=False)

    description: Mapped[str | None] = mapped_column(String(500))

    priority: Mapped[TaskPriority] = mapped_column(
        Enum(TaskPriority, name="task_priority", create_constraint=True),
        nullable=False,
        default=TaskPriority.Medium,
    )

    tag: Mapped[TeamRole | None] = mapped_column(
        Enum(TeamRole, name="team_role", create_constraint=True)
    )

    status: Mapped[TaskStatus] = mapped_column(
        Enum(TaskStatus), nullable=False, default=TaskStatus.ToDo
    )

    seq: Mapped[int] = mapped_column(SmallInteger, nullable=False)

    key: Mapped[str] = mapped_column(String(32), nullable=False)

    deadline: Mapped[DateTime] = mapped_column(DateTime, nullable=False)

    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=func.now()
    )

    updated_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=func.now(), onupdate=func.now()
    )
