from fastapi import APIRouter, Request, Response, status

from src.modules.auth.schemas.user import UserLoginRequest, UserTokenPair
from src.modules.auth.services.UserService import UserAuthService

router = APIRouter(prefix="/auth/user", tags=["auth(user)"])


@router.post("/login", response_model=UserTokenPair, status_code=status.HTTP_200_OK)
async def login(
    request: Request,
    data: UserLoginRequest,
    response: Response,
) -> UserTokenPair:
    return await UserAuthService.login(request, data, response)


@router.post("/refresh", response_model=UserTokenPair, status_code=status.HTTP_200_OK)
async def refresh(request: Request, response: Response) -> UserTokenPair:
    return UserAuthService.refresh(request, response)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(response: Response) -> None:
    UserAuthService.logout(response)
