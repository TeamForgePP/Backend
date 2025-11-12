from __future__ import annotations

from uuid import uuid4

from sqlalchemy import String, Text, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..base import Base


class Report(Base):
    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)

    file_url: Mapped[str] = mapped_column(Text, nullable=False)

    creator_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    editor_id: Mapped[UUID | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    teacher_note: Mapped[str | None] = mapped_column(Text)

    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )

    creator: Mapped["User"] = relationship(
        "User",
        back_populates="created_reports",
        primaryjoin="Report.creator_id==foreign(User.id)",
    )
    editor: Mapped["User | None"] = relationship(
        "User",
        back_populates="edited_reports",
        primaryjoin="Report.editor_id==foreign(User.id)",
    )

    project_links: Mapped[list["ProjectReport"]] = relationship(
        "ProjectReport", back_populates="report", cascade="all, delete-orphan"
    )
    projects: Mapped[list["Project"]] = relationship(
        "Project", secondary="project_reports", back_populates="reports", viewonly=True
    )