from uuid import UUID

from fastapi import APIRouter, status

from src.modules.notifications.services import NotificationsService
from src.modules.notifications.shemas import InvitationResponse

router = APIRouter(prefix="/invitation", tags=["invitations"])


@router.get(
    "/{invitation_id}",
    response_model=InvitationResponse,
    status_code=status.HTTP_200_OK,
    name="get_notifications_info",
)
async def get_invitation_info(invitation_id: UUID) -> InvitationResponse:
    return await NotificationsService.get_invitation_info(invitation_id)
