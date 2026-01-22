from uuid import UUID

from fastapi import APIRouter, Depends, status

from src.core.security.dependencies import PrincipalContext, require_user_or_admin
from src.modules.notifications.services import NotificationsService
from src.modules.notifications.shemas import BasicResponse, NotificationsResponse

router = APIRouter(prefix="/notifications", tags=["notifications"])
user_dep = Depends(require_user_or_admin)


@router.get(
    "",
    response_model=NotificationsResponse,
    status_code=status.HTTP_200_OK,
    name="get_notifications",
)
async def get_notifications_info(_user: PrincipalContext = user_dep) -> NotificationsResponse:
    return await NotificationsService.get_notifications_info(UUID(_user.sub))


@router.patch(
    "/read-all",
    response_model=BasicResponse,
    status_code=status.HTTP_200_OK,
    name="read_all_notifications",
)
async def read_all(_user: PrincipalContext = user_dep) -> BasicResponse:
    return await NotificationsService.read_all(UUID(_user.sub))
