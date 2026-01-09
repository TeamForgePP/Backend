from typing import Annotated

from fastapi import APIRouter, Depends, status

from src.core.security.dependencies import PrincipalContext, principal_context_dep
from src.modules.profile.schemas.profile import ProfileResponse, ProfileUpdateRequest
from src.modules.profile.services.ProfileService import ProfileService

router = APIRouter(prefix="/profile", tags=["profile"])
PrincipalDep = Annotated[PrincipalContext, Depends(principal_context_dep)]


@router.get(
    "",
    response_model=ProfileResponse,
    status_code=status.HTTP_200_OK,
)
async def get_profile(
    principal: PrincipalDep,
) -> ProfileResponse:
    return await ProfileService.get_profile(principal)


@router.patch(
    "",
    response_model=ProfileResponse,
    status_code=status.HTTP_200_OK,
)
async def update_profile(
    data: ProfileUpdateRequest,
    principal: PrincipalDep,
) -> ProfileResponse:
    return await ProfileService.update_profile(principal, data)
