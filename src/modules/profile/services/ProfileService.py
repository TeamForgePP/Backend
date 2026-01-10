from __future__ import annotations

from uuid import UUID

from fastapi import HTTPException, status

from src.core.db.UnitOfWork import get_uow
from src.core.logger import get_logger
from src.core.security.dependencies import PrincipalContext
from src.modules.profile.schemas.profile import ProfileResponse, ProfileUpdateRequest

logger = get_logger("modules.profile")


class ProfileService:
    @staticmethod
    async def _get_user_safe(uow, user_id: UUID):
        user = await uow.users.get_by_id(user_id)
        if user is None:
            logger.warning("User %s not found when accessing profile", user_id)
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )
        return user

    @staticmethod
    def _build_full_name(user) -> str:
        parts: list[str] = []
        if user.last_name:
            parts.append(user.last_name)
        if user.first_name:
            parts.append(user.first_name)
        if user.patronymic:
            parts.append(user.patronymic)
        return " ".join(parts)

    @staticmethod
    async def _build_profile_response(uow, user) -> ProfileResponse:
        group_name: str | None = None
        if getattr(user, "group_id", None) is not None:
            group = await uow.groups.get_by_id(user.group_id)
            if group is not None:
                group_name = group.name
        teams: list[str] = []

        return ProfileResponse(
            full_name=ProfileService._build_full_name(user),
            group=group_name,
            role=str(user.user_type.value),
            teams=teams,
            email=user.email,
        )

    @staticmethod
    async def get_profile(principal: PrincipalContext) -> ProfileResponse:
        user_id = UUID(principal.sub)

        async with get_uow() as uow:
            user = await ProfileService._get_user_safe(uow, user_id)
            return await ProfileService._build_profile_response(uow, user)

    @staticmethod
    async def update_profile(
        principal: PrincipalContext,
        data: ProfileUpdateRequest,
    ) -> ProfileResponse:
        user_id = UUID(principal.sub)

        async with get_uow() as uow:
            user = await ProfileService._get_user_safe(uow, user_id)

            # Обновляем только те поля, которые реально пришли
            if data.last_name is not None:
                user.last_name = data.last_name

            if data.first_name is not None:
                user.first_name = data.first_name

            if data.patronymic is not None:
                user.patronymic = data.patronymic

            if data.email is not None:
                user.email = data.email

            await uow.session.flush()
            await uow.commit()

            logger.info("User %s updated profile", user_id)

            return await ProfileService._build_profile_response(uow, user)
