from __future__ import annotations

from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.db.interfaces import BaseRepository
from src.core.db.models import Users


class UsersRepo(BaseRepository):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def get_by_id(self, id_: UUID) -> Users | None:
        result = await self._session.execute(select(Users).where(Users.id == id_))
        return result.scalar_one_or_none()

    async def get_all(self) -> list[Users]:
        result = await self._session.execute(select(Users))
        return list(result.scalars().all())

    async def create(self, data: dict[str, Any]) -> Users:
        user = Users(**data)
        self._session.add(user)
        await self._session.flush()
        await self._session.refresh(user)
        return user

    async def update(self, id_: UUID, data: dict[str, Any]) -> Users | None:
        result = await self._session.execute(select(Users).where(Users.id == id_))
        user = result.scalar_one_or_none()
        if user is None:
            return None

        for field, value in data.items():
            setattr(user, field, value)

        await self._session.flush()
        await self._session.refresh(user)
        return user

    async def delete(self, id_: UUID) -> bool:
        result = await self._session.execute(select(Users).where(Users.id == id_))
        user = result.scalar_one_or_none()
        if user is None:
            return False

        await self._session.delete(user)
        await self._session.flush()
        return True

    # Доп. методы:

    async def get_by_group(self, group_id: UUID) -> list[Users]:
        result = await self._session.execute(select(Users).where(Users.group_id == group_id))
        return list(result.scalars().all())
