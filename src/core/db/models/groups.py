from uuid import UUID, uuid4

from sqlalchemy import DateTime, Enum, ForeignKey, SmallInteger, String, func
from sqlalchemy.orm import Mapped, mapped_column

from src.core.db.base import Base
from src.core.db.enums import Faculty, LevelEducation


class Groups(Base):
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)

    name: Mapped[str] = mapped_column(
        String(11),
        unique=True,
        nullable=False,
        doc="сокращенное название группы, например: БПИ-2402",
    )

    level_ed: Mapped[LevelEducation] = mapped_column(
        Enum(LevelEducation, name="level_education", create_constraint=True),
        nullable=False,
    )

    faculty: Mapped[Faculty] = mapped_column(
        Enum(Faculty, name="faculty", create_constraint=True),
        nullable=False,
    )

    year_adm: Mapped[int] = mapped_column(SmallInteger, nullable=False)

    curator_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        doc="староста",
        index=True,
    )

    students_count: Mapped[int] = mapped_column(SmallInteger, nullable=False, default="0")

    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=func.now()
    )

    updated_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=func.now(), onupdate=func.now()
    )
