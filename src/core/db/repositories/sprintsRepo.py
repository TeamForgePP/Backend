from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.db.interfaces import BaseRepository
from src.core.db.models.sprints import Sprints


class SprintsRepo(BaseRepository):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def get_by_id(self, id_: UUID) -> Sprints | None:
        """Получить объект по id или вернуть None."""

        sprint = await self._session.execute(select(Sprints).where(Sprints.id == id_))
        return sprint.scalar_one_or_none()

    async def get_all(self) -> list[Sprints]:
        """Получить все объекты."""

        all_sprints = await self._session.execute(select(Sprints))
        return list(all_sprints.scalars().all())

    async def create(self, data: dict[str, Any]) -> Sprints:
        """Создать объект из словаря полей и вернуть его."""

        sprint = Sprints()
        for key, value in data.items():
            setattr(sprint, key, value)

        self._session.add(sprint)
        await self._session.commit()
        await self._session.refresh(sprint)
        return sprint

    async def update(self, id_: UUID, data: dict[str, Any]) -> Sprints | None:
        """Обновить объект по id, вернуть обновлённый объект или None."""

        sprint = await self._session.execute(select(Sprints).where(Sprints.id == id_))
        result = sprint.scalar_one_or_none()

        if result is None:
            return None

        for key, value in data.items():
            setattr(result, key, value)

        await self._session.commit()
        await self._session.refresh(result)
        return result

    async def delete(self, id_: UUID) -> bool:
        """Удалить объект по id. Вернуть True, если удалён, иначе False."""

        sprint = await self._session.execute(select(Sprints).where(Sprints.id == id_))
        result = sprint.scalar_one_or_none()

        if result is None:
            return False

        await self._session.delete(result)
        await self._session.commit()
        return True
