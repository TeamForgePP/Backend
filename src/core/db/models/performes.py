from uuid import UUID

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from src.core.db import Base


class Performes(Base):
    task_id: Mapped[UUID] = mapped_column(ForeignKey("tasks.id"), nullable=False)

    assigne_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
