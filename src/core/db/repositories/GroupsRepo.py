from __future__ import annotations

from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.db.interfaces import BaseRepository
from src.core.db.models import Groups


class GroupsRepo(BaseRepository):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def get_by_id(self, id_: UUID) -> Groups | None:
        result = await self._session.execute(select(Groups).where(Groups.id == id_))
        return result.scalar_one_or_none()

    async def get_all(self) -> list[Groups]:
        result = await self._session.execute(select(Groups))
        return list(result.scalars().all())

    async def create(self, data: dict[str, Any]) -> Groups:
        group = Groups(**data)
        self._session.add(group)
        await self._session.flush()
        await self._session.refresh(group)
        return group

    async def update(self, id_: UUID, data: dict[str, Any]) -> Groups | None:
        result = await self._session.execute(select(Groups).where(Groups.id == id_))
        group = result.scalar_one_or_none()
        if group is None:
            return None

        for field, value in data.items():
            setattr(group, field, value)

        await self._session.flush()
        await self._session.refresh(group)
        return group

    async def delete(self, id_: UUID) -> bool:
        result = await self._session.execute(select(Groups).where(Groups.id == id_))
        group = result.scalar_one_or_none()
        if group is None:
            return False

        await self._session.delete(group)
        await self._session.flush()
        return True
