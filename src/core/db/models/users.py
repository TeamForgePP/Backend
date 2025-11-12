from __future__ import annotations

from uuid import uuid4

from sqlalchemy import String, Text, Boolean, DateTime, ForeignKey, Enum, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..base import Base
from ..enums import UserRole


class User(Base):
    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)

    last_name: Mapped[str] = mapped_column(String(35), nullable=False)
    first_name: Mapped[str] = mapped_column(String(35), nullable=False)
    patronymic: Mapped[str | None] = mapped_column(String(35))

    email: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    password: Mapped[str] = mapped_column(String(128), nullable=False)  # под длину хеша

    user_type: Mapped[UserRole] = mapped_column(Enum(UserRole, name="user_role", create_constraint=True), nullable=False)

    avatar_url: Mapped[str | None] = mapped_column(Text)

    group_id: Mapped[UUID | None] = mapped_column(ForeignKey("groups.id", ondelete="SET NULL"))
    in_team: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="false")

    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )

    group: Mapped["Group | None"] = relationship(back_populates="members")

    curated_groups: Mapped[list["Group"]] = relationship(
        "Group",
        back_populates="curator",
        primaryjoin="User.id==foreign(Group.curator_id)",
    )

    lead_projects: Mapped[list["Project"]] = relationship(
        "Project",
        back_populates="teamlead",
        primaryjoin="User.id==foreign(Project.teamlead_id)",
    )
    curated_projects: Mapped[list["Project"]] = relationship(
        "Project",
        back_populates="curator",
        primaryjoin="User.id==foreign(Project.curator_id)",
    )

    created_reports: Mapped[list["Report"]] = relationship(
        "Report",
        back_populates="creator",
        primaryjoin="User.id==foreign(Report.creator_id)",
    )
    edited_reports: Mapped[list["Report"]] = relationship(
        "Report",
        back_populates="editor",
        primaryjoin="User.id==foreign(Report.editor_id)",
    )