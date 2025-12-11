from collections.abc import AsyncIterator
from typing import Annotated

from fastapi import APIRouter, Depends, Request, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.db.repositories.UsersRepo import UsersRepo
from src.core.db.session import get_async_session
from src.modules.auth.schemas.user import UserLoginRequest, UserTokenPair
from src.modules.auth.services.UserService import UserAuthService

router = APIRouter(prefix="/auth/user", tags=["user-auth"])


SessionDep = Annotated[AsyncSession, Depends(get_async_session)]


async def get_users_repo(
    session: SessionDep,
) -> AsyncIterator[UsersRepo]:
    repo = UsersRepo(session)
    try:
        yield repo
    finally:
        ...


UsersRepoDep = Annotated[UsersRepo, Depends(get_users_repo)]


@router.post("/login", response_model=UserTokenPair)
async def login(
    request: Request,
    data: UserLoginRequest,
    response: Response,
    users_repo: UsersRepoDep,
) -> UserTokenPair:
    return await UserAuthService.login(request, data, response, users_repo)


@router.post("/refresh", response_model=UserTokenPair)
async def refresh(request: Request, response: Response) -> UserTokenPair:
    return UserAuthService.refresh(request, response)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(response: Response) -> None:
    return UserAuthService.logout(response)
