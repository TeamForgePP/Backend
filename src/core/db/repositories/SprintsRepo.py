from typing import Any, cast
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.db.interfaces import BaseRepository
from src.core.db.models.sprints import Sprints


class SprintsRepo(BaseRepository):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)
        self._session: AsyncSession = session

    async def get_by_id(self, sprint_id: UUID) -> Sprints | None:
        sprint = await self._session.get(Sprints, sprint_id)
        return cast(Sprints | None, sprint)

    async def get_by_project_id(self, project_id: UUID) -> list[Sprints]:
        result = await self._session.execute(
            select(Sprints).where(Sprints.project_id == project_id).order_by(Sprints.seq)
        )
        sprints = result.scalars().all()
        return cast(list[Sprints], sprints)

    async def get_all(self) -> list[Sprints]:
        result = await self._session.execute(select(Sprints))
        sprints = result.scalars().all()
        return cast(list[Sprints], sprints)

    async def create(self, data: dict[str, Any]) -> Sprints:
        sprint = Sprints(**data)
        self._session.add(sprint)
        await self._session.flush()
        await self._session.refresh(sprint)
        return sprint

    async def update(self, sprint_id: UUID, data: dict[str, Any]) -> Sprints | None:
        sprint = await self.get_by_id(sprint_id)
        if sprint is None:
            return None

        for field, value in data.items():
            setattr(sprint, field, value)

        await self._session.flush()
        await self._session.refresh(sprint)
        return sprint

    async def delete(self, sprint_id: UUID) -> bool:
        sprint = await self.get_by_id(sprint_id)
        if sprint is None:
            return False

        await self._session.delete(sprint)
        await self._session.flush()
        return True
