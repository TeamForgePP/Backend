from typing import Any, cast
from uuid import UUID

from sqlalchemy import delete as sql_delete
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.db.interfaces import BaseRepository
from src.core.db.models import Teams


class TeamsRepo(BaseRepository):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)
        self._session: AsyncSession = session

    async def get_by_id(self, team_id: UUID) -> Teams | None:
        team = await self._session.get(Teams, team_id)
        return cast(Teams | None, team)

    async def get_by_project(self, project_id: UUID) -> list[Teams]:
        result = await self._session.execute(select(Teams).where(Teams.project_id == project_id))
        teams = result.scalars().all()
        return cast(list[Teams], teams)

    async def get_all(self) -> list[Teams]:
        result = await self._session.execute(select(Teams))
        teams = result.scalars().all()
        return cast(list[Teams], teams)

    async def create(self, data: dict[str, Any]) -> Teams:
        team = Teams(**data)
        self._session.add(team)
        await self._session.flush()
        await self._session.refresh(team)
        return team

    async def update(self, team_id: UUID, data: dict[str, Any]) -> Teams | None:
        team = await self.get_by_id(team_id)
        if team is None:
            return None

        for field, value in data.items():
            setattr(team, field, value)

        await self._session.flush()
        await self._session.refresh(team)
        return team

    async def delete(self, team_id: UUID) -> bool:
        team = await self.get_by_id(team_id)
        if team is None:
            return False

        await self._session.delete(team)
        await self._session.flush()
        return True

    async def delete_member(self, project_id: UUID, user_id: UUID) -> bool:
        result = await self._session.execute(
            sql_delete(Teams).where(Teams.project_id == project_id, Teams.user_id == user_id)
        )
        await self._session.flush()
        return (result.rowcount or 0) > 0

    async def delete_by_project_id(self, project_id: UUID) -> bool:
        result = await self._session.execute(
            sql_delete(Teams).where(Teams.project_id == project_id)
        )
        await self._session.flush()
        return (result.rowcount or 0) > 0
