from typing import Any, cast
from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.db.enums import TeamRole
from src.core.db.models import ProjectRole


class ProjectRoleRepo:
    def __init__(self, session: AsyncSession) -> None:
        self._session: AsyncSession = session

    async def get_roles_for_user_in_project(
        self,
        project_id: UUID,
        user_id: UUID,
    ) -> list[TeamRole]:
        result = await self._session.execute(
            select(ProjectRole.role).where(
                ProjectRole.project_id == project_id,
                ProjectRole.user_id == user_id,
            )
        )
        roles = result.scalars().all()
        return cast(list[TeamRole], roles)

    async def get_all_for_user_in_project(
        self,
        project_id: UUID,
        user_id: UUID,
    ) -> list[ProjectRole]:
        result = await self._session.execute(
            select(ProjectRole).where(
                ProjectRole.project_id == project_id,
                ProjectRole.user_id == user_id,
            )
        )
        relations = result.scalars().all()
        return cast(list[ProjectRole], relations)

    async def add_role(
        self,
        project_id: UUID,
        user_id: UUID,
        role: TeamRole,
    ) -> ProjectRole:
        data: dict[str, Any] = {
            "project_id": project_id,
            "user_id": user_id,
            "role": role,
        }
        relation = ProjectRole(**data)
        self._session.add(relation)

        try:
            await self._session.flush()
            await self._session.refresh(relation)
            return relation
        except IntegrityError:
            await self._session.rollback()
            result = await self._session.execute(
                select(ProjectRole).where(
                    ProjectRole.project_id == project_id,
                    ProjectRole.user_id == user_id,
                    ProjectRole.role == role,
                )
            )
            existing = result.scalar_one()
            return cast(ProjectRole, existing)

    async def delete_role(
        self,
        project_id: UUID,
        user_id: UUID,
        role: TeamRole,
    ) -> bool:
        result = await self._session.execute(
            delete(ProjectRole).where(
                ProjectRole.project_id == project_id,
                ProjectRole.user_id == user_id,
                ProjectRole.role == role,
            )
        )
        await self._session.flush()
        return (result.rowcount or 0) > 0

    async def delete_all_roles(self, project_id: UUID, user_id: UUID) -> bool:
        result = await self._session.execute(
            delete(ProjectRole).where(
                ProjectRole.project_id == project_id, ProjectRole.user_id == user_id
            )
        )
        await self._session.flush()
        return (result.rowcount or 0) > 0
