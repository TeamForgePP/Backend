from uuid import UUID, uuid4

from sqlalchemy import DateTime, Enum, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column

from src.core.db.base import Base
from src.core.db.enums import InvitationStatus


class Invitations(Base):
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)

    notification_id: Mapped[UUID] = mapped_column(ForeignKey("notifications.id"), nullable=False)

    project_id: Mapped[UUID] = mapped_column(ForeignKey("projects.id"), nullable=False)

    invited_user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id"), nullable=False, doc="тот, кого пригласили"
    )

    invited_by_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id"), nullable=False, doc="тот, кто пригласил"
    )

    status: Mapped[InvitationStatus] = mapped_column(
        Enum(InvitationStatus, name="invitation_status", create_constraint=True),
        nullable=False,
        default=InvitationStatus.Posted,
    )

    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=func.now()
    )

    updated_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=func.now(), onupdate=func.now()
    )
