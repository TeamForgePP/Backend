import logging
from typing import cast
from uuid import UUID

from fastapi import HTTPException, status

from src.core.db import UnitOfWork, get_uow
from src.core.db.models import Users
from src.core.logger import get_logger
from src.modules.admin.schemas import (
    UserCreate,
    UserRead,
    UserUpdate,
)
from src.modules.admin.utils import hash_password, user_to_read_model

logger = get_logger("admin.user.service")
logger.setLevel(logging.INFO)


class UserService:
    # ---------------- CREATE ---------------- #

    @classmethod
    async def create_user(cls, data: UserCreate) -> UserRead:
        async with get_uow() as uow:
            try:
                return await cls._create_user_in_uow(uow, data)
            except Exception as e:
                logger.error("Error during user creation: %s", str(e))
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Internal Server Error during user creation",
                ) from e

    @classmethod
    async def _create_user_in_uow(cls, uow: UnitOfWork, data: UserCreate) -> UserRead:
        logger.info("create_user started | email=%s", data.email)

        existing_user = await uow.users.get_by_email(data.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email already exists",
            )

        user_data = data.model_dump(exclude={"password"})
        user_data["password"] = hash_password(data.password)

        user = await uow.users.create(user_data)
        await uow.commit()

        # user should be Users; cast to satisfy mypy if repo returns Optional[Users]
        return user_to_read_model(cast(Users, user))

    # ---------------- GET ---------------- #

    @classmethod
    async def get_user_by_id(cls, user_id: UUID) -> UserRead:
        async with get_uow() as uow:
            user = await uow.users.get_by_id(user_id)
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found",
                )
            return user_to_read_model(cast(Users, user))

    @classmethod
    async def get_user_by_email(cls, email: str) -> UserRead:
        async with get_uow() as uow:
            user = await uow.users.get_by_email(email)
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found",
                )
            return user_to_read_model(cast(Users, user))

    # ---------------- UPDATE ---------------- #

    @classmethod
    async def update_user(cls, user_id: UUID, data: UserUpdate) -> UserRead:
        async with get_uow() as uow:
            logger.info("update_user started | user_id=%s", user_id)

            user = await uow.users.get_by_id(user_id)
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found",
                )

            update_data = data.model_dump(exclude_unset=True)

            if "email" in update_data:
                exists = await uow.users.get_by_email(update_data["email"])
                if exists and exists.id != user_id:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="User with this email already exists",
                    )

            if "password" in update_data:
                update_data["password"] = hash_password(update_data["password"])

            updated_user = await uow.users.update(user_id, update_data)
            await uow.commit()

            return user_to_read_model(cast(Users, updated_user))

    # ---------------- DELETE ---------------- #

    @classmethod
    async def delete_user(cls, user_id: UUID) -> None:
        async with get_uow() as uow:
            logger.info("delete_user started | user_id=%s", user_id)

            deleted = await uow.users.delete(user_id)
            if not deleted:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found",
                )

            await uow.commit()
