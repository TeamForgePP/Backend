from uuid import UUID

from fastapi import APIRouter, Depends, status

from src.core.security.dependencies import AccessContext, require_admin
from src.modules.admin.schemas import (
    UserCreate,
    UserPasswordUpdate,
    UserProfileUpdate,
    UserRead,
)
from src.modules.admin.services import UserService

router = APIRouter(prefix="/user", tags=["admin"])

admin_dep = Depends(require_admin)


@router.post("", response_model=UserRead, status_code=status.HTTP_201_CREATED, name="create_user")
async def create_user(
    data: UserCreate,
    _admin: AccessContext = admin_dep,
) -> UserRead:
    return await UserService.create_user(data)


@router.get("/{user_id}", response_model=UserRead, status_code=status.HTTP_200_OK, name="get_user")
async def get_user_by_id(
    user_id: UUID,
    _admin: AccessContext = admin_dep,
) -> UserRead:
    return await UserService.get_user_by_id(user_id)


@router.get(
    "/by-email/{email}",
    response_model=UserRead,
    status_code=status.HTTP_200_OK,
    name="get_user_by_email",
)
async def get_user_by_email(
    email: str,
    _admin: AccessContext = admin_dep,
) -> UserRead:
    return await UserService.get_user_by_email(email)


@router.patch("/", response_model=UserRead, status_code=status.HTTP_200_OK, name="update_user")
async def update_user(
    data: UserProfileUpdate,
    _admin: AccessContext = admin_dep,
) -> UserRead:
    return await UserService.update_user(data)


@router.patch(
    "/password",
    response_model=UserRead,
    status_code=status.HTTP_200_OK,
    name="update_user_password",
)
async def update_user_password(
    data: UserPasswordUpdate,
    _admin: AccessContext = admin_dep,
) -> UserRead:
    return await UserService.update_user_password(data)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT, name="delete_user")
async def delete_user(
    user_id: UUID,
    _admin: AccessContext = admin_dep,
) -> None:
    await UserService.delete_user(user_id)
