from __future__ import annotations

from uuid import uuid4

from sqlalchemy import String, Text, Boolean, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..base import Base


class Project(Base):
    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)

    teamlead_id: Mapped[UUID | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    curator_id: Mapped[UUID | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)

    is_completed: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="false")
    avatar_url: Mapped[str | None] = mapped_column(Text)
    github_url: Mapped[str | None] = mapped_column(Text)

    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )

    teamlead: Mapped["User | None"] = relationship(
        "User",
        back_populates="lead_projects",
        primaryjoin="Project.teamlead_id==foreign(User.id)",
    )
    curator: Mapped["User | None"] = relationship(
        "User",
        back_populates="curated_projects",
        primaryjoin="Project.curator_id==foreign(User.id)",
    )

    sprints: Mapped[list["Sprint"]] = relationship(back_populates="project", cascade="all, delete-orphan")

    # связь с отчетами через таблицу связей
    project_reports: Mapped[list["ProjectReport"]] = relationship(
        back_populates="project", cascade="all, delete-orphan"
    )
    reports: Mapped[list["Report"]] = relationship(
        "Report",
        secondary="project_reports",
        back_populates="projects",
        viewonly=True,
    )
