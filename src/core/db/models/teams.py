from uuid import UUID as pyUUID
from uuid import uuid4

from sqlalchemy import DateTime, Enum, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from ..base import Base
from .enum import UserStatus


class Teams(Base):
    id: Mapped[pyUUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    # project_id: Mapped[pyUUID] = mapped_column(UUID(as_uuid=True),
    #   ForeignKey("projects.id"),
    #   nullable=False)
    # user_id: Mapped[pyUUID] = mapped_column(UUID(as_uuid=True),
    #   ForeignKey("users.id"),
    #   nullable=False)
    status: Mapped[UserStatus] = mapped_column(Enum(UserStatus), nullable=False)
    updated_at: Mapped[DateTime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), onupdate=func.now()
    )
