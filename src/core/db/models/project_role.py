# from uuid import UUID as pyUUID

from sqlalchemy import Enum
from sqlalchemy.orm import Mapped, mapped_column

from ..base import Base
from .enum import TeamRole


class ProjectRole(Base):
    # project_id: Mapped[pyUUID] = mapped_column(
    #   UUID(as_uuid=True),
    #   ForeignKey("projects.id"),
    #   nullable=False)

    # user_id: Mapped[pyUUID] = mapped_column(
    #   UUID(as_uuid=True),
    #   ForeignKey("users.id"),
    #   nullable=False)

    role: Mapped[TeamRole] = mapped_column(Enum(TeamRole), nullable=False)
