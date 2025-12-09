from typing import Any, cast
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.db.interfaces import BaseRepository
from src.core.db.models.groups import Groups


class GroupsRepo(BaseRepository):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)
        self._session: AsyncSession = session

    async def get_by_id(self, group_id: UUID) -> Groups | None:
        group = await self._session.get(Groups, group_id)
        return cast(Groups | None, group)

    async def get_all(self) -> list[Groups]:
        result = await self._session.execute(select(Groups))
        groups = result.scalars().all()
        return cast(list[Groups], groups)

    async def create(self, data: dict[str, Any]) -> Groups:
        group = Groups(**data)
        self._session.add(group)
        await self._session.flush()
        await self._session.refresh(group)
        return group

    async def update(self, group_id: UUID, data: dict[str, Any]) -> Groups | None:
        group = await self.get_by_id(group_id)
        if group is None:
            return None

        for field, value in data.items():
            setattr(group, field, value)

        await self._session.flush()
        await self._session.refresh(group)
        return group

    async def delete(self, group_id: UUID) -> bool:
        group = await self.get_by_id(group_id)
        if group is None:
            return False

        await self._session.delete(group)
        await self._session.flush()
        return True
