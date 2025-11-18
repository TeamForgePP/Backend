from __future__ import annotations

from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.db.interfaces import BaseRepository
from src.core.db.models import Teams


class TeamsRepo(BaseRepository):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def get_by_id(self, id_: UUID) -> Teams | None:
        result = await self._session.execute(select(Teams).where(Teams.id == id_))
        return result.scalar_one_or_none()

    async def get_all(self) -> list[Teams]:
        result = await self._session.execute(select(Teams))
        return list(result.scalars().all())

    async def create(self, data: dict[str, Any]) -> Teams:
        team = Teams(**data)
        self._session.add(team)
        await self._session.flush()
        await self._session.refresh(team)
        return team

    async def update(self, id_: UUID, data: dict[str, Any]) -> Teams | None:
        result = await self._session.execute(select(Teams).where(Teams.id == id_))
        team = result.scalar_one_or_none()
        if team is None:
            return None

        for field, value in data.items():
            setattr(team, field, value)

        await self._session.flush()
        await self._session.refresh(team)
        return team

    async def delete(self, id_: UUID) -> bool:
        result = await self._session.execute(select(Teams).where(Teams.id == id_))
        team = result.scalar_one_or_none()
        if team is None:
            return False

        await self._session.delete(team)
        await self._session.flush()
        return True

        # Доп. метод

    async def get_by_project(self, project_id: UUID) -> list[Teams]:
        result = await self._session.execute(select(Teams).where(Teams.project_id == project_id))
        return list(result.scalars().all())
