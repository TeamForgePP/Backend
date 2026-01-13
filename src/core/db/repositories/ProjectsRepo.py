from typing import Any, cast
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.db.interfaces import BaseRepository
from src.core.db.models import Projects, Teams


class ProjectsRepo(BaseRepository):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)
        self._session: AsyncSession = session

    async def get_by_id(self, project_id: UUID) -> Projects | None:
        project = await self._session.get(Projects, project_id)
        return cast(Projects | None, project)

    async def get_by_name(self, name: str) -> Projects | None:
        result = await self._session.execute(select(Projects).where(Projects.name == name))
        return cast(Projects | None, result.scalar_one_or_none())

    async def get_projects_id_by_user_id(self, user_id: UUID) -> list[Projects]:
        projects_id = (
            (await self._session.execute(select(Teams.project_id).where(Teams.user_id == user_id)))
            .scalars()
            .all()
        )
        if not projects_id:
            return []
        projects_result = (
            (await self._session.execute(select(Projects).where(Projects.id.in_(projects_id))))
            .scalars()
            .all()
        )
        return cast(list[Projects], projects_result)

    async def get_all(self) -> list[Projects]:
        result = await self._session.execute(select(Projects))
        projects = result.scalars().all()
        return cast(list[Projects], projects)

    async def get_all_uncompleted_projects(self) -> list[Projects]:
        result = await self._session.execute(
            select(Projects).where(Projects.is_completed.is_(False))
        )
        projects = result.scalars().all()
        return cast(list[Projects], projects)

    async def create(self, data: dict[str, Any]) -> Projects:
        project = Projects(**data)
        self._session.add(project)
        await self._session.flush()
        await self._session.refresh(project)
        return project

    async def update(self, project_id: UUID, data: dict[str, Any]) -> Projects | None:
        project = await self.get_by_id(project_id)
        if project is None:
            return None

        for field, value in data.items():
            setattr(project, field, value)

        await self._session.flush()
        await self._session.refresh(project)
        return project

    async def delete(self, project_id: UUID) -> bool:
        project = await self.get_by_id(project_id)
        if project is None:
            return False

        await self._session.delete(project)
        await self._session.flush()
        return True
