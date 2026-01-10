from typing import Annotated

from fastapi import APIRouter, Depends, status

from src.core.security.dependencies import PrincipalContext, require_user_or_admin
from src.modules.profile.schemas.profile import ProfileResponse, ProfileUpdateRequest
from src.modules.profile.services.ProfileService import ProfileService

router = APIRouter(prefix="/profile", tags=["profile"])

PrincipalContextDep = Annotated[PrincipalContext, Depends(require_user_or_admin)]


@router.get(
    path="",
    response_model=ProfileResponse,
    status_code=status.HTTP_200_OK,
)
async def get_profile(
    principal: PrincipalContextDep,
) -> ProfileResponse:
    return await ProfileService.get_profile(principal)


@router.patch(
    path="",
    response_model=ProfileResponse,
    status_code=status.HTTP_200_OK,
)
async def update_profile(
    data: ProfileUpdateRequest,
    principal: PrincipalContextDep,
) -> ProfileResponse:
    return await ProfileService.update_profile(principal, data)
