from uuid import UUID

from sqlalchemy import Enum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from src.core.db import Base, TeamRole


class ProjectRole(Base):
    project_id: Mapped[UUID] = mapped_column(ForeignKey("projects.id"), nullable=False)

    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), nullable=False)

    role: Mapped[TeamRole] = mapped_column(
        Enum(TeamRole, name="team_role", create_constraint=True), nullable=False
    )
