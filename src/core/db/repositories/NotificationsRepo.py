from typing import Any, cast
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.db.interfaces import BaseRepository
from src.core.db.models.notifications import Notifications


class NotificationsRepo(BaseRepository):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)
        self._session: AsyncSession = session

    async def get_by_id(self, notification_id: UUID) -> Notifications | None:
        notification = await self._session.get(Notifications, notification_id)
        return cast(Notifications | None, notification)

    async def get_all(self) -> list[Notifications]:
        result = await self._session.execute(select(Notifications))
        notifications = result.scalars().all()
        return cast(list[Notifications], notifications)

    async def get_by_user_id(self, user_id: UUID) -> list[Notifications]:
        result = await self._session.execute(
            select(Notifications)
            .where(Notifications.user_id == user_id)
            .order_by(Notifications.created_at.desc())
        )
        notifications = result.scalars().all()
        return cast(list[Notifications], notifications)

    async def create(self, data: dict[str, Any]) -> Notifications:
        notification = Notifications(**data)
        self._session.add(notification)
        await self._session.flush()
        await self._session.refresh(notification)
        return notification

    async def update(
        self,
        notification_id: UUID,
        data: dict[str, Any],
    ) -> Notifications | None:
        notification = await self.get_by_id(notification_id)
        if notification is None:
            return None

        for field, value in data.items():
            setattr(notification, field, value)

        await self._session.flush()
        await self._session.refresh(notification)
        return notification

    async def delete(self, notification_id: UUID) -> bool:
        notification = await self.get_by_id(notification_id)
        if notification is None:
            return False

        await self._session.delete(notification)
        await self._session.flush()
        return True
