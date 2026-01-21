from uuid import UUID

from fastapi import APIRouter, Depends, status

from src.core.security.dependencies import PrincipalContext, require_user_or_admin
from src.modules.notifications.services import InvitationsService
from src.modules.notifications.shemas import BasicResponse, InvitationResponse

router = APIRouter(
    prefix="/invitations",
    tags=["invitations"],
)

user_dep = Depends(require_user_or_admin)


@router.get(
    "/{notification_id}",
    response_model=InvitationResponse,
    status_code=status.HTTP_200_OK,
    name="get_invitation_by_notification_id",
)
async def get_invitation_info(
    notification_id: UUID,
    _user: PrincipalContext = user_dep,
) -> InvitationResponse:
    return await InvitationsService.get_invitation_info(
        notification_id=notification_id,
        user_id=UUID(_user.sub),
    )


@router.post(
    "/{notification_id}/accept",
    response_model=BasicResponse,
    status_code=status.HTTP_200_OK,
    name="accept_invitation",
)
async def accept_invitation(
    notification_id: UUID,
    _user: PrincipalContext = user_dep,
) -> BasicResponse:
    return await InvitationsService.accept_invitation(
        notification_id=notification_id,
        user_id=UUID(_user.sub),
    )


@router.post(
    "/{notification_id}/reject",
    response_model=BasicResponse,
    status_code=status.HTTP_200_OK,
    name="reject_invitation",
)
async def reject_invitation(
    notification_id: UUID,
    _user: PrincipalContext = user_dep,
) -> BasicResponse:
    return await InvitationsService.reject_invitation(
        notification_id=notification_id,
        user_id=UUID(_user.sub),
    )
