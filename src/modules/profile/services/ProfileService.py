from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select

from src.core.db.models.groups import Groups
from src.core.db.models.teams import Teams
from src.core.db.models.users import Users
from src.core.db.UnitOfWork import get_uow
from src.core.logger import get_logger
from src.core.security.dependencies import PrincipalContext
from src.modules.profile.schemas.profile import ProfileResponse, ProfileUpdateRequest

logger = get_logger("modules.profile")


class ProfileService:
    @classmethod
    async def get_profile(cls, principal: PrincipalContext) -> ProfileResponse:
        user_id = cls._get_user_id_from_principal(principal)

        async with get_uow() as uow:
            db_user = await uow.users.get_by_id(user_id)
            if db_user is None:
                logger.error("User %s not found in DB", user_id)
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="user not found",
                )

            group_name, team_names = await cls._load_group_and_teams(uow, db_user)

        return cls._build_profile_response(db_user, group_name, team_names)

    @classmethod
    async def update_profile(
        cls,
        principal: PrincipalContext,
        data: ProfileUpdateRequest,
    ) -> ProfileResponse:
        user_id = cls._get_user_id_from_principal(principal)

        async with get_uow() as uow:
            db_user = await uow.users.get_by_id(user_id)
            if db_user is None:
                logger.error("User %s not found in DB", user_id)
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="user not found",
                )

            if data.first_name is not None:
                db_user.first_name = data.first_name

            if data.last_name is not None:
                db_user.last_name = data.last_name

            if data.patronymic is not None:
                db_user.patronymic = data.patronymic

            if data.group_id is not None:
                # проверяем, что такая группа существует
                group_result = await uow.session.execute(
                    select(Groups.id).where(Groups.id == data.group_id),
                )
                if group_result.first() is None:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="group not found",
                    )
                db_user.group_id = data.group_id

            await uow.session.flush()
            await uow.session.refresh(db_user)

            group_name, team_names = await cls._load_group_and_teams(uow, db_user)

        return cls._build_profile_response(db_user, group_name, team_names)

    @staticmethod
    def _get_user_id_from_principal(principal: PrincipalContext) -> UUID:
        if principal.role != "user":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="only users have profile",
            )

        try:
            return UUID(principal.sub)
        except ValueError as exc:
            logger.error("Invalid user id in token subject: %s", principal.sub)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="invalid token subject",
            ) from exc

    @staticmethod
    async def _load_group_and_teams(
        uow,
        user: Users,
    ) -> tuple[str | None, list[str]]:
        group_name: str | None = None
        team_names: list[str] = []

        if user.group_id is not None:
            group_result = await uow.session.execute(
                select(Groups.name).where(Groups.id == user.group_id),
            )
            group_row = group_result.first()
            if group_row is not None:
                group_name = group_row[0]

            teams_result = await uow.session.execute(
                select(Teams.name).where(Teams.group_id == user.group_id),
            )
            team_names = [row[0] for row in teams_result.all()]

        return group_name, team_names

    @staticmethod
    def _build_profile_response(
        user: Users,
        group_name: str | None,
        team_names: list[str],
    ) -> ProfileResponse:
        patronymic_part = f" {user.patronymic}" if user.patronymic else ""
        full_name = f"{user.last_name} {user.first_name}{patronymic_part}"

        return ProfileResponse(
            full_name=full_name,
            group=group_name,
            role=None,  # роль команды/проекта можно будет добавить позже
            teams=team_names,
            email=user.email,
        )
