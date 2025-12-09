from uuid import UUID

from sqlalchemy import Enum, ForeignKey, PrimaryKeyConstraint
from sqlalchemy.orm import Mapped, mapped_column

from src.core.db.base import Base
from src.core.db.enums import TeamRole


class ProjectRole(Base):
    __table_args__ = (
        PrimaryKeyConstraint("project_id", "user_id", "role", name="pk_project_role"),
    )

    project_id: Mapped[UUID] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    role: Mapped[TeamRole] = mapped_column(
        Enum(TeamRole, name="team_role", create_constraint=True),
        nullable=False,
    )
