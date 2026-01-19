from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select

from src.core.db.enums import TeamRole, UserStatus
from src.core.db.models.groups import Groups
from src.core.db.models.projects import Projects
from src.core.db.models.teams import Teams
from src.core.db.models.users import Users
from src.core.db.UnitOfWork import UnitOfWork, get_uow
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

            group_name = await cls._load_group_name(uow, db_user)
            team_names, role_value = await cls._load_team_and_role(uow, db_user)

        return cls._build_profile_response(db_user, group_name, team_names, role_value)

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

            group_name = await cls._load_group_name(uow, db_user)
            team_names, role_value = await cls._load_team_and_role(uow, db_user)

        return cls._build_profile_response(db_user, group_name, team_names, role_value)

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
    async def _load_group_name(uow: UnitOfWork, user: Users) -> str | None:
        if user.group_id is None:
            return None

        result = await uow.session.execute(
            select(Groups.name).where(Groups.id == user.group_id),
        )
        row = result.first()
        return row[0] if row is not None else None

    @staticmethod
    async def _load_team_and_role(
        uow: UnitOfWork,
        user: Users,
    ) -> tuple[list[str], str | None]:
        if not user.in_team:
            return ["-"], "-"

        team_result = await uow.session.execute(
            select(Teams.project_id).where(
                Teams.user_id == user.id,
                Teams.status == UserStatus.Member,
            ),
        )
        project_ids = [row[0] for row in team_result.all()]

        if not project_ids:
            return ["-"], "-"

        projects_result = await uow.session.execute(
            select(Projects).where(
                Projects.id.in_(project_ids),
                Projects.is_completed.is_(False),
            ),
        )
        projects = projects_result.scalars().all()

        if not projects:
            return ["-"], "-"

        active_project = projects[0]
        team_names = [active_project.name]

        roles: list[TeamRole] = await uow.project_roles.get_roles_for_user_in_project(
            user.id,
            active_project.id,
        )

        if not roles:
            role_value: str | None = "-"
        else:
            role_value = ", ".join(role.value.upper() for role in roles)

        return team_names, role_value

    @staticmethod
    def _build_profile_response(
        user: Users,
        group_name: str | None,
        team_names: list[str],
        role_value: str | None,
    ) -> ProfileResponse:
        patronymic_part = f" {user.patronymic}" if user.patronymic else ""
        full_name = f"{user.last_name} {user.first_name}{patronymic_part}"

        return ProfileResponse(
            full_name=full_name,
            group=group_name,
            role=role_value,
            teams=team_names,
            email=user.email,
        )
