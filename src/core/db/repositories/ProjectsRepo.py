from __future__ import annotations

from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.db.interfaces import BaseRepository
from src.core.db.models import Projects


class ProjectsRepo(BaseRepository):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def get_by_id(self, id_: UUID) -> Projects | None:
        result = await self._session.execute(select(Projects).where(Projects.id == id_))
        return result.scalar_one_or_none()

    async def get_all(self) -> list[Projects]:
        result = await self._session.execute(select(Projects))
        return list(result.scalars().all())

    async def create(self, data: dict[str, Any]) -> Projects:
        project = Projects(**data)
        self._session.add(project)
        await self._session.flush()
        await self._session.refresh(project)
        return project

    async def update(self, id_: UUID, data: dict[str, Any]) -> Projects | None:
        result = await self._session.execute(select(Projects).where(Projects.id == id_))
        project = result.scalar_one_or_none()
        if project is None:
            return None

        for field, value in data.items():
            setattr(project, field, value)

        await self._session.flush()
        await self._session.refresh(project)
        return project

    async def delete(self, id_: UUID) -> bool:
        result = await self._session.execute(select(Projects).where(Projects.id == id_))
        project = result.scalar_one_or_none()
        if project is None:
            return False

        await self._session.delete(project)
        await self._session.flush()
        return True
