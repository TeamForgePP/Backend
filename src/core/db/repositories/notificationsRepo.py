from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.db.interfaces import BaseRepository
from src.core.db.models.notifications import Notifications


class NotificationsRepo(BaseRepository):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def get_by_id(self, id_: UUID) -> Notifications | None:
        """Получить объект по id или вернуть None."""

        notification = await self._session.execute(
            select(Notifications).where(Notifications.id == id_)
        )
        return notification.scalar_one_or_none()

    async def get_all(self) -> list[Notifications]:
        """Получить все объекты."""

        all_notifications = await self._session.execute(select(Notifications))
        return list(all_notifications.scalars().all())

    async def create(self, data: dict[str, Any]) -> Notifications:
        """Создать объект из словаря полей и вернуть его."""

        notification = Notifications()
        for key, value in data.items():
            setattr(notification, key, value)

        self._session.add(notification)
        await self._session.commit()
        await self._session.refresh(notification)
        return notification

    async def update(self, id_: UUID, data: dict[str, Any]) -> Notifications | None:
        """Обновить объект по id, вернуть обновлённый объект или None."""

        notification = await self._session.execute(
            select(Notifications).where(Notifications.id == id_)
        )
        result = notification.scalar_one_or_none()

        if result is None:
            return None

        for key, value in data.items():
            setattr(result, key, value)

        await self._session.commit()
        await self._session.refresh(result)
        return result

    async def delete(self, id_: UUID) -> bool:
        """Удалить объект по id. Вернуть True, если удалён, иначе False."""

        notification = await self._session.execute(
            select(Notifications).where(Notifications.id == id_)
        )
        result = notification.scalar_one_or_none()

        if result is None:
            return False

        await self._session.delete(result)
        await self._session.commit()
        return True
