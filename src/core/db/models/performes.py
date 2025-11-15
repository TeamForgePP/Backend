from uuid import UUID as pyUUID

from sqlalchemy import ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from ..base import Base


class Performes(Base):
    task_id: Mapped[pyUUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tasks.id"), nullable=False
    )


#   assigne_id: Mapped[pyUUID] = mapped_column(
#       UUID(as_uuid=True),
#       ForeignKey("users.id"),
#       nullable=False)
