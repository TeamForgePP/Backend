from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.db.interfaces import BaseRepository
from src.core.db.models.tasks import Tasks


class TasksRepo(BaseRepository):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def get_by_id(self, id_: UUID) -> Tasks | None:
        """Получить объект по id или вернуть None."""

        task = await self._session.execute(select(Tasks).where(Tasks.id == id_))
        return task.scalar_one_or_none()

    async def get_all(self) -> list[Tasks]:
        """Получить все объекты."""

        all_tasks = await self._session.execute(select(Tasks))
        return list(all_tasks.scalars().all())

    async def create(self, data: dict[str, Any]) -> Tasks:
        """Создать объект из словаря полей и вернуть его."""

        task = Tasks()
        for key, value in data.items():
            setattr(task, key, value)

        self._session.add(task)
        await self._session.commit()
        await self._session.refresh(task)
        return task

    async def update(self, id_: UUID, data: dict[str, Any]) -> Tasks | None:
        """Обновить объект по id, вернуть обновлённый объект или None."""

        task = await self._session.execute(select(Tasks).where(Tasks.id == id_))
        result = task.scalar_one_or_none()

        if result is None:
            return None

        for key, value in data.items():
            setattr(result, key, value)

        await self._session.commit()
        await self._session.refresh(result)
        return result

    async def delete(self, id_: UUID) -> bool:
        """Удалить объект по id. Вернуть True, если удалён, иначе False."""

        task = await self._session.execute(select(Tasks).where(Tasks.id == id_))
        result = task.scalar_one_or_none()

        if result is None:
            return False

        await self._session.delete(result)
        await self._session.commit()
        return True
