from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select

from src.core.db.models.teams import Teams
from src.core.db.UnitOfWork import get_uow
from src.core.logger import get_logger
from src.core.security.dependencies import PrincipalContext
from src.modules.profile.schemas.profile import ProfileResponse, ProfileUpdateRequest

logger = get_logger("profile.user")


class ProfileService:
    @classmethod
    async def _ensure_user_role(cls, principal: PrincipalContext) -> None:
        if principal.role != "user":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="profile is available only for user role",
            )

    @classmethod
    def _parse_user_id(cls, principal: PrincipalContext) -> UUID:
        try:
            return UUID(principal.sub)
        except ValueError as exc:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="invalid subject in token",
            ) from exc

    @staticmethod
    def _build_full_name(user) -> str:
        parts = [user.last_name, user.first_name, user.patronymic]
        return " ".join(p for p in parts if p)

    @staticmethod
    def _to_response(user, group, teams: list[Teams]) -> ProfileResponse:
        return ProfileResponse(
            full_name=ProfileService._build_full_name(user),
            group=group.name if group else None,
            role=str(user.role),
            teams=[team.name for team in teams],
            email=user.email,
        )

    @classmethod
    async def _load_teams_for_user(cls, uow, user) -> list[Teams]:
        result = await uow.session.execute(select(Teams).where(Teams.group_id == user.group_id))
        return list(result.scalars().all())

    @classmethod
    async def get_profile(cls, principal: PrincipalContext) -> ProfileResponse:
        cls._ensure_user_role(principal)
        user_id = cls._parse_user_id(principal)

        async with get_uow() as uow:
            user = await uow.users.get_by_id(user_id)
            if user is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="user not found",
                )

            group = None
            if user.group_id is not None:
                group = await uow.groups.get_by_id(user.group_id)

            teams = await cls._load_teams_for_user(uow, user)

        return cls._to_response(user, group, teams)

    @classmethod
    async def update_profile(
        cls,
        principal: PrincipalContext,
        data: ProfileUpdateRequest,
    ) -> ProfileResponse:
        cls._ensure_user_role(principal)
        user_id = cls._parse_user_id(principal)

        update_data = data.model_dump(exclude_none=True)
        if not update_data:
            return await cls.get_profile(principal)

        async with get_uow() as uow:
            user = await uow.users.update(user_id, update_data)
            if user is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="user not found",
                )

            group = None
            if user.group_id is not None:
                group = await uow.groups.get_by_id(user.group_id)

            teams = await cls._load_teams_for_user(uow, user)

        return cls._to_response(user, group, teams)
