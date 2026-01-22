from dataclasses import dataclass
from uuid import UUID

from fastapi import HTTPException, status

from src.core.db import NotificationType, UnitOfWork
from src.core.db.models.invitations import Invitations
from src.core.db.models.notifications import Notifications


@dataclass(frozen=True)
class InvitationContext:
    notification: Notifications
    invitation: Invitations


class InvitationUtils:
    @classmethod
    async def load_invitation_context(
        cls,
        uow: UnitOfWork,
        notification_id: UUID,
        user_id: UUID,
    ) -> InvitationContext:
        notification = await uow.notifications.get_by_id(notification_id=notification_id)
        if not notification:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Notification not found",
            )

        if notification.type != NotificationType.NewInvite:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="This notification does not contain an invitation",
            )

        invitation = await uow.invitations.get_by_notification_id(notification_id=notification_id)
        if not invitation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Invitation not found",
            )

        if invitation.invited_user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions",
            )

        return InvitationContext(
            notification=notification,
            invitation=invitation,
        )
