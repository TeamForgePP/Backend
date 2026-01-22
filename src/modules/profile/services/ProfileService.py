from typing import cast
from uuid import UUID

from fastapi import HTTPException, status
from pydantic import EmailStr
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
            try:
                user = await uow.users.get_by_id(user_id)
                if user is None:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="user not found",
                    )

                group_name = await cls._load_group_name(uow, user)
                active_project, role_value = await cls._load_active_project_and_role(uow, user)

                return cls._build_profile_response(user, group_name, active_project, role_value)

            except HTTPException:
                raise
            except Exception as exc:
                logger.exception("Error during get_profile")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Internal Server Error during get profile",
                ) from exc

    @classmethod
    async def update_profile(
        cls,
        principal: PrincipalContext,
        data: ProfileUpdateRequest,
    ) -> ProfileResponse:
        user_id = cls._get_user_id_from_principal(principal)

        async with get_uow() as uow:
            try:
                user = await uow.users.get_by_id(user_id)
                if user is None:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="user not found",
                    )

                if data.first_name is not None:
                    user.first_name = data.first_name

                if data.last_name is not None:
                    user.last_name = data.last_name

                if data.patronymic is not None:
                    user.patronymic = data.patronymic

                if data.group_id is not None:
                    group_exists = await uow.session.execute(
                        select(Groups.id).where(Groups.id == data.group_id)
                    )
                    if group_exists.first() is None:
                        raise HTTPException(
                            status_code=status.HTTP_404_NOT_FOUND,
                            detail="group not found",
                        )
                    user.group_id = data.group_id

                await uow.session.flush()
                await uow.session.refresh(user)
                await uow.commit()

                group_name = await cls._load_group_name(uow, user)
                active_project, role_value = await cls._load_active_project_and_role(uow, user)

                return cls._build_profile_response(user, group_name, active_project, role_value)

            except HTTPException:
                raise
            except Exception as exc:
                logger.exception("Error during update_profile")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Internal Server Error during update profile",
                ) from exc

    @staticmethod
    def _get_user_id_from_principal(principal: PrincipalContext) -> UUID:
        if principal.role != "user":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="only users have profile",
            )

        try:
            return UUID(principal.sub)
        except (ValueError, TypeError) as exc:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="invalid token subject",
            ) from exc

    @staticmethod
    async def _load_group_name(uow: UnitOfWork, user: Users) -> str | None:
        if not isinstance(user.group_id, UUID):
            return None

        result = await uow.session.execute(select(Groups.name).where(Groups.id == user.group_id))
        row = result.first()
        return cast(str | None, row[0] if row else None)

    @staticmethod
    async def _load_active_project_and_role(
        uow: UnitOfWork,
        user: Users,
    ) -> tuple[str | None, str | None]:
        team_result = await uow.session.execute(
            select(Teams.project_id).where(
                Teams.user_id == user.id,
                Teams.status.in_([UserStatus.Owner, UserStatus.Member]),
            )
        )
        project_ids = [row[0] for row in team_result.all()]

        if not project_ids:
            return None, "-"

        project_result = await uow.session.execute(
            select(Projects).where(
                Projects.id.in_(project_ids),
                Projects.is_completed.is_(False),
            )
        )
        projects = project_result.scalars().all()

        if not projects:
            return None, "-"

        if len(projects) > 1:
            logger.warning(
                "User %s has %d active projects, expected 1",
                user.id,
                len(projects),
            )

        active_project = projects[0]

        roles: list[TeamRole] = await uow.project_roles.get_roles_for_user_in_project(
            active_project.id,  # порядок ВАЖЕН
            user.id,
        )

        role_value = ", ".join(role.value.upper() for role in roles) if roles else "-"

        return active_project.name, role_value

    @staticmethod
    def _build_profile_response(
        user: Users,
        group_name: str | None,
        active_project: str | None,
        role_value: str | None,
    ) -> ProfileResponse:
        patronymic_part = f" {user.patronymic}" if user.patronymic else ""
        full_name = f"{user.last_name} {user.first_name} {patronymic_part}".strip()

        return ProfileResponse(
            full_name=full_name,
            group=group_name,
            role=role_value,
            active_project=active_project,
            email=cast(EmailStr, user.email),
        )
