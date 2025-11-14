from __future__ import annotations

from uuid import UUID, uuid4

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, SmallInteger, String, func
from sqlalchemy.orm import Mapped, mapped_column

from ..base import Base
from ..enums import Faculty, LevelEducation


class Group(Base):
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)

    name: Mapped[str | None] = mapped_column(String(11))

    level_ed: Mapped[LevelEducation] = mapped_column(
        Enum(LevelEducation, name="level_education", create_constraint=True), nullable=False
    )

    faculty: Mapped[Faculty] = mapped_column(
        Enum(Faculty, name="faculty", create_constraint=True), nullable=False
    )

    year_adm: Mapped[int] = mapped_column(SmallInteger, nullable=False)

    curator_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"), nullable=False
    )

    students: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")

    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )
