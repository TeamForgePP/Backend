from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.db.interfaces import BaseRepository
from src.core.db.models.invitations import Invitations


class InvitationsRepo(BaseRepository):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def get_by_id(self, id_: UUID) -> Invitations | None:
        """Получить объект по id или вернуть None."""

        invitation = await self._session.execute(select(Invitations).where(Invitations.id == id_))
        return invitation.scalar_one_or_none()

    async def get_all(self) -> list[Invitations]:
        """Получить все объекты."""

        all_invitations = await self._session.execute(select(Invitations))
        return list(all_invitations.scalars().all())

    async def create(self, data: dict[str, Any]) -> Invitations:
        """Создать объект из словаря полей и вернуть его."""

        invitation = Invitations()
        for key, value in data.items():
            setattr(invitation, key, value)

        self._session.add(invitation)
        await self._session.commit()
        await self._session.refresh(invitation)
        return invitation

    async def update(self, id_: UUID, data: dict[str, Any]) -> Invitations | None:
        """Обновить объект по id, вернуть обновлённый объект или None."""

        invitation = await self._session.execute(select(Invitations).where(Invitations.id == id_))
        result = invitation.scalar_one_or_none()

        if result is None:
            return None

        for key, value in data.items():
            setattr(result, key, value)

        await self._session.commit()
        await self._session.refresh(result)
        return result

    async def delete(self, id_: UUID) -> bool:
        """Удалить объект по id. Вернуть True, если удалён, иначе False."""

        invitation = await self._session.execute(select(Invitations).where(Invitations.id == id_))
        result = invitation.scalar_one_or_none()

        if result is None:
            return False

        await self._session.delete(result)
        await self._session.commit()
        return True
