from __future__ import annotations

from uuid import uuid4

from sqlalchemy import String, SmallInteger, Integer, DateTime, ForeignKey, Enum, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..base import Base
from ..enums import LevelEducation, Faculty


class Group(Base):
    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)

    name: Mapped[str] = mapped_column(String(37), nullable=False)

    level_ed: Mapped[LevelEducation] = mapped_column(
        Enum(LevelEducation, name="level_education", create_constraint=True), nullable=False
    )
    faculty: Mapped[Faculty] = mapped_column(Enum(Faculty, name="faculty", create_constraint=True), nullable=False)

    year_adm: Mapped[int | None] = mapped_column(SmallInteger)
    curator_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    students: Mapped[int | None] = mapped_column(Integer)

    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )

    curator: Mapped["User"] = relationship(back_populates="curated_groups")
    members: Mapped[list["User"]] = relationship(back_populates="group")
