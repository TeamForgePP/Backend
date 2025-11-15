from uuid import UUID as pyUUID
from uuid import uuid4

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import UUID as UUID
from sqlalchemy.orm import Mapped, mapped_column

from ..base import Base
from .enum import TaskPriority, TaskStatus, TeamRole


class Tasks(Base):
    id: Mapped[pyUUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)

    project_id: Mapped[pyUUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False
    )

    sprint_id: Mapped[pyUUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("sprints.id"), nullable=False
    )

    title: Mapped[str] = mapped_column(String(100), nullable=False)

    description: Mapped[str] = mapped_column(Text, nullable=False)

    priority: Mapped[TaskPriority] = mapped_column(Enum(TaskPriority), nullable=False)

    tag: Mapped[TeamRole] = mapped_column(Enum(TeamRole))

    status: Mapped[TaskStatus] = mapped_column(
        Enum(TaskStatus), nullable=False, default=TaskStatus.ToDo
    )

    seq: Mapped[int] = mapped_column(Integer, nullable=False)

    key: Mapped[str] = mapped_column(String(32), nullable=False)

    deadline: Mapped[DateTime] = mapped_column(DateTime, nullable=False)

    created_at: Mapped[DateTime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )

    updated_at: Mapped[DateTime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), onupdate=func.now()
    )
