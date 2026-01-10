from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select

from src.core.db.models import Groups, Teams, Users
from src.core.db.UnitOfWork import UnitOfWork, get_uow
from src.core.logger import get_logger
from src.core.security.dependencies import PrincipalContext
from src.modules.profile.schemas.profile import ProfileResponse, ProfileUpdateRequest

logger = get_logger("modules.profile")


class ProfileService:
    @staticmethod
    def _build_full_name(user: Users) -> str:
        parts = [user.last_name, user.first_name, user.patronymic]
        return " ".join(part for part in parts if part)

    @classmethod
    async def _get_user_with_relations(
        cls,
        uow: UnitOfWork,
        user_id: UUID,
    ) -> tuple[Users, Groups | None, list[Teams]]:
        user = await uow.users.get_by_id(user_id)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="user not found",
            )

        group: Groups | None = None
        teams: list[Teams] = []

        if user.group_id is not None:
            group = await uow.groups.get_by_id(user.group_id)

            result = await uow.session.execute(select(Teams).where(Teams.group_id == user.group_id))
            teams = list(result.scalars().all())

        return user, group, teams

    @classmethod
    async def get_profile(cls, principal: PrincipalContext) -> ProfileResponse:
        user_id = UUID(principal.sub)

        async with get_uow() as uow:
            user, group, teams = await cls._get_user_with_relations(uow, user_id)

        full_name = cls._build_full_name(user)
        group_name = group.name if group is not None else None
        team_names = [team.name for team in teams]

        role_value: str | None = None
        if hasattr(user, "role") and user.role is not None:
            role_value = getattr(user.role, "value", None) or str(user.role)

        return ProfileResponse(
            full_name=full_name,
            group=group_name,
            role=role_value,
            teams=team_names,
            email=user.email,
        )

    @classmethod
    async def update_profile(
        cls,
        principal: PrincipalContext,
        data: ProfileUpdateRequest,
    ) -> ProfileResponse:
        user_id = UUID(principal.sub)

        async with get_uow() as uow:
            user = await uow.users.get_by_id(user_id)
            if user is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="user not found",
                )

            if data.last_name is not None:
                user.last_name = data.last_name
            if data.first_name is not None:
                user.first_name = data.first_name
            if getattr(data, "patronymic", None) is not None:
                user.patronymic = data.patronymic
            if data.email is not None:
                user.email = data.email

            await uow.commit()

            group, teams = None, []
            if user.group_id is not None:
                group = await uow.groups.get_by_id(user.group_id)
                result = await uow.session.execute(
                    select(Teams).where(Teams.group_id == user.group_id)
                )
                teams = list(result.scalars().all())

        full_name = cls._build_full_name(user)
        group_name = group.name if group is not None else None
        team_names = [team.name for team in teams]

        role_value: str | None = None
        if hasattr(user, "role") and user.role is not None:
            role_value = getattr(user.role, "value", None) or str(user.role)

        return ProfileResponse(
            full_name=full_name,
            group=group_name,
            role=role_value,
            teams=team_names,
            email=user.email,
        )
