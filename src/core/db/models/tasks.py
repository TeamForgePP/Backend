from anyio.abc import TaskStatus
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Enum, text, ForeignKey, String, Integer, Date, Text
from sqlalchemy.dialects.postgresql import UUID
from uuid import uuid4
from enum import Enum as Enumm
from src.core.db.base import Base
from src.core.db.models.project_role import TeamRole


class TaskPriority(Enumm):
    High = "high"
    Medium = "medium"
    Low = "Low"

class TaskStatus(Enumm):
    ToDo = "TO_DO"
    InProgress = "IN_PROGRESS"
    InTest = "IN_TEST"
    InReview = "IN_REVIEW"
    Done = "DONE"
class Tasks(Base):
    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    # project_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False)
    # sprint_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("sprints.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    priority: Mapped[TaskPriority] = mapped_column(Enum(TaskPriority), nullable=False)
    tag: Mapped[TeamRole] = mapped_column(Enum(TeamRole))
    status: Mapped[TaskStatus] = mapped_column(Enum(TaskStatus), nullable=False, default=TaskStatus.ToDo)
    seq: Mapped[int] = mapped_column(Integer, nullable=False)
    key: Mapped[str] = mapped_column(String(32), nullable=False)
    deadline: Mapped[Date] = mapped_column(Date, nullable=False)
    created_at: Mapped[Date] = mapped_column(Date, nullable=False, default=text("now()"))
    updated_at: Mapped[Date] = mapped_column(Date, nullable=False, default=text("now()"))