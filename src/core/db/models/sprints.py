from __future__ import annotations

from uuid import uuid4

from sqlalchemy import String, Text, Integer, Date, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..base import Base


class Sprint(Base):
    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)

    project_id: Mapped[UUID] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)

    seq: Mapped[int] = mapped_column(Integer, nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    goal: Mapped[str | None] = mapped_column(String(150))

    start: Mapped[Date | None] = mapped_column(Date)
    deadline: Mapped[Date | None] = mapped_column(Date)

    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    project: Mapped["Project"] = relationship(back_populates="sprints")