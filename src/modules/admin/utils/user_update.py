from typing import cast

from fastapi import HTTPException, status

from src.core.db import get_uow
from src.core.db.models import Users
from src.modules.admin.schemas import UserPasswordUpdate, UserProfileUpdate, UserRead
from src.modules.admin.utils import user_to_read_model
from src.modules.admin.utils.user_hash import hash_password


async def update_user_profile(data: UserProfileUpdate) -> UserRead:
    async with get_uow() as uow:
        if data.email is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email is required",
            )

        user = await uow.users.get_by_email(data.email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        update_data = data.model_dump(exclude_unset=True)

        if "email" in update_data:
            new_email = update_data["email"]
            if new_email is None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email cannot be null",
                )

            if new_email != user.email:
                exists = await uow.users.get_by_email(new_email)
                if exists and exists.id != user.id:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="User with this email already exists",
                    )

        updated_user = await uow.users.update(user.id, update_data)
        await uow.commit()

    return user_to_read_model(cast(Users, updated_user))


async def update_user_password(data: UserPasswordUpdate) -> UserRead:
    async with get_uow() as uow:
        if data.email is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email is required",
            )

        user = await uow.users.get_by_email(data.email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        hashed_password = hash_password(data.password)

        updated_user = await uow.users.update(user.id, {"password": hashed_password})
        await uow.commit()

    return user_to_read_model(cast(Users, updated_user))
